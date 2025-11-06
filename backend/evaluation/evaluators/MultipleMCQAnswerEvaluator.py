from evaluation.evaluators.AnswerEvaluator import AnswerEvaluator
from evaluation.models import QuestionAttempt


class MultipleMCQAnswerEvaluator(AnswerEvaluator):

    def __init__(self, question_attempt: QuestionAttempt):
        super().__init__(question_attempt)

    def evaluate(self):
        questions = self.question_attempt.question.question_data["questions"]
        eval_data = []

        for i in range(len(questions)):
            question_eval_data = {
                "is_correct": (
                    i < len(self.question_attempt.multiple_mcq_answer)
                    and questions[i]["answer"]
                    == self.question_attempt.multiple_mcq_answer[i]
                )
            }
            eval_data.append(question_eval_data)

        self.question_attempt.eval_data = eval_data
        self.question_attempt.status = QuestionAttempt.Status.EVALUATED
        self.question_attempt.save()
