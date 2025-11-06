from evaluation.event_flow.processors.base_event_processor import EventProcessor
from evaluation.models import AttemptResponseEvaluation, QuestionAttempt


class AbortHandler(EventProcessor):

    def initialize(self):
        self.evaluation_id = self.root_arguments.get("evaluation_id")
        self.question_attempt_id = self.root_arguments.get("question_attempt_id")

    def _execute(self):
        self.initialize()

        # Try to find AttemptResponseEvaluation first (for IELTS/Interview evaluations)
        try:
            eval_object = AttemptResponseEvaluation.objects.get(id=self.evaluation_id)
            eval_object.summary = {"text": "Evaluation was aborted"}
            eval_object.status = AttemptResponseEvaluation.Status.ERROR
            eval_object.save()
            self.log_info(
                f"Updated AttemptResponseEvaluation {self.evaluation_id} with abort status"
            )
        except AttemptResponseEvaluation.DoesNotExist:
            self.log_info(
                f"AttemptResponseEvaluation {self.evaluation_id} not found, trying QuestionAttempt"
            )

            # If not found, try to update QuestionAttempt (for Speaking/Writing evaluations)
            if self.question_attempt_id:
                try:
                    question_attempt = QuestionAttempt.objects.get(
                        id=self.question_attempt_id
                    )

                    # Update eval_data to indicate evaluation was aborted
                    eval_data = question_attempt.eval_data or {}
                    eval_data["aborted"] = True
                    eval_data["abort_reason"] = (
                        "Evaluation was aborted due to processor error"
                    )

                    question_attempt.eval_data = eval_data
                    question_attempt.status = (
                        QuestionAttempt.Status.ATTEMPTED
                    )  # Reset to attempted
                    question_attempt.save()

                    self.log_info(
                        f"Updated QuestionAttempt {self.question_attempt_id} with abort status"
                    )
                except QuestionAttempt.DoesNotExist:
                    self.log_error(
                        f"Neither AttemptResponseEvaluation {self.evaluation_id} nor QuestionAttempt {self.question_attempt_id} found"
                    )
            else:
                self.log_error(
                    f"AttemptResponseEvaluation {self.evaluation_id} not found and no question_attempt_id provided"
                )

        return {}
