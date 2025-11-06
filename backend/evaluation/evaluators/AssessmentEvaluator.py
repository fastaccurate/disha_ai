import logging
from evaluation.models import AssessmentAttempt, Question, QuestionAttempt

logger = logging.getLogger(__name__)


class AssessmentEvaluator:
    MCQ_POINTS = 1
    MCQ_INCORRECT_POINTS = 0
    WRITING_MAX_POINTS = 100

    def __init__(self, assessment_attempt: AssessmentAttempt):
        self.assessment_attempt = assessment_attempt

    def _should_start_evaluation(self):
        logger.info(
            f"🔍🔍🔍 _should_start_evaluation() called for assessment {self.assessment_attempt.assessment_id} 🔍🔍🔍"
        )
        logger.info(f"🔍🔍🔍 closed: {self.assessment_attempt.closed} 🔍🔍🔍")
        logger.info(
            f"🔍🔍🔍 evaluation_triggered: {self.assessment_attempt.evaluation_triggered} 🔍🔍🔍"
        )
        logger.info(f"🔍🔍🔍 status: {self.assessment_attempt.status} 🔍🔍🔍")

        if (
            self.assessment_attempt.closed
            and not self.assessment_attempt.evaluation_triggered
            and self.assessment_attempt.status
            != int(AssessmentAttempt.Status.ABANDONED)
        ):

            count_of_unevaluated_questions = (
                QuestionAttempt.objects.filter(
                    assessment_attempt_id=self.assessment_attempt.assessment_id
                )
                .exclude(
                    status__in=[
                        QuestionAttempt.Status.EVALUATED,
                        QuestionAttempt.Status.NOT_ATTEMPTED,
                    ]
                )
                .count()
            )

            logger.info(
                f"🔍🔍🔍 count_of_unevaluated_questions: {count_of_unevaluated_questions} 🔍🔍🔍"
            )

            if count_of_unevaluated_questions > 0:
                logger.info(f"🔍🔍🔍 Has unevaluated questions. 🔍🔍🔍")
                return False
            logger.info(f"🔍🔍🔍 No unevaluated questions. 🔍🔍🔍")
            return True

        logger.info(f"🔍🔍🔍 Initial conditions not met. 🔍🔍🔍")
        return False

    def evaluate(self):
        if not self._should_start_evaluation():
            return
        logger.info(f"🔍🔍🔍 Starting ASSESSMENT EVALUATOR evaluation. 🔍🔍🔍")
        score = 0
        max_score = 0
        overall_percentage = 0

        writing_score = 0
        writing_grammar_score = 0
        writing_coherence_score = 0
        writing_vocab_score = 0
        writing_max_score = 0

        attempted_questions = QuestionAttempt.objects.filter(
            assessment_attempt_id=self.assessment_attempt.assessment_id
        ).all()

        questions_data = self.assessment_attempt.question_list

        list_section_wise_score = []

        for sections in questions_data:
            section_wise_score = 0
            section_wise_max_score = 0

            for question_id in sections["questions"]:
                question = Question.objects.filter(id=question_id).first()
                question_attempt = attempted_questions.filter(
                    question_id=question_id
                ).first()
                if question_attempt:
                    answer_type = question_attempt.question.answer_type
                    question_eval_data = question_attempt.eval_data

                    if answer_type == int(Question.AnswerType.MCQ):
                        if question_eval_data["is_correct"]:
                            section_wise_score += AssessmentEvaluator.MCQ_POINTS
                        else:
                            section_wise_score += (
                                AssessmentEvaluator.MCQ_INCORRECT_POINTS
                            )

                        section_wise_max_score += AssessmentEvaluator.MCQ_POINTS

                    if answer_type == int(Question.AnswerType.MMCQ):
                        for item in question_eval_data:
                            if item["is_correct"]:
                                section_wise_score += AssessmentEvaluator.MCQ_POINTS
                            else:
                                section_wise_score += (
                                    AssessmentEvaluator.MCQ_INCORRECT_POINTS
                                )

                            section_wise_max_score += AssessmentEvaluator.MCQ_POINTS
                        no_of_questions = len(question.question_data["questions"])

                    if answer_type == int(Question.AnswerType.SUBJECTIVE):
                        writing_score += question_eval_data["final_score"]
                        writing_grammar_score += question_eval_data["grammar"].get(
                            "score", None
                        )
                        writing_coherence_score += question_eval_data["coherence"].get(
                            "score", None
                        )
                        writing_vocab_score += question_eval_data["vocab"].get(
                            "score", None
                        )
                        writing_max_score += AssessmentEvaluator.WRITING_MAX_POINTS

                        section_wise_score += question_eval_data["final_score"]
                        section_wise_max_score += AssessmentEvaluator.WRITING_MAX_POINTS

                        logger.info(
                            f"🔍 Writing scores updated - final: {question_eval_data['final_score']}, grammar: {question_eval_data['grammar'].get('score')}"
                        )
                else:
                    if question.answer_type == int(Question.AnswerType.MCQ):
                        section_wise_max_score += AssessmentEvaluator.MCQ_POINTS
                    if question.answer_type == int(Question.AnswerType.MMCQ):
                        no_of_questions = len(question.question_data["questions"])
                        section_wise_max_score += (
                            AssessmentEvaluator.MCQ_POINTS * no_of_questions
                        )
                    if question.answer_type == int(Question.AnswerType.SUBJECTIVE):
                        section_wise_max_score += AssessmentEvaluator.WRITING_MAX_POINTS

            score += section_wise_score
            max_score += section_wise_max_score

            normalized_score = (
                round((section_wise_score * 100) / section_wise_max_score, 2)
                if section_wise_score > 0
                else 0
            )
            overall_percentage += normalized_score

            list_section_wise_score.append(
                {
                    "name": sections["section"],
                    "max_score": section_wise_max_score,
                    "score": section_wise_score,
                    "percentage": normalized_score,
                }
            )

        overall_normalized_score = round(overall_percentage / len(questions_data), 1)
        additional_data = {
            "writing_score": writing_score,
            "writing_grammar_score": writing_grammar_score,
            "writing_coherence_score": writing_coherence_score,
            "writing_vocab_score": writing_vocab_score,
            "writing_max_score": writing_max_score,
            "sections": list_section_wise_score,
        }

        performance_tag = "OUTSTANDING"
        if overall_normalized_score >= 70 and overall_normalized_score < 85:
            performance_tag = "COMPETENT"
        elif overall_normalized_score >= 55:
            performance_tag = "GOOD"
        elif overall_normalized_score >= 40:
            performance_tag = "AVERAGE"
        elif overall_normalized_score < 40:
            performance_tag = "UNSATISFACTORY"

        eval_data = {
            "additional_data": additional_data,
            "percentage": overall_normalized_score,
            "max_score": max_score,
            "total_score": score,
            "performance_tag": performance_tag,
        }

        self.assessment_attempt.eval_data = eval_data

        self.assessment_attempt.status = AssessmentAttempt.Status.COMPLETED
        self.assessment_attempt.evaluation_triggered = True

        self.assessment_attempt.save()
