import logging
from evaluation.evaluators.AnswerEvaluator import AnswerEvaluator
from evaluation.models import QuestionAttempt

logger = logging.getLogger(__name__)


class MCQAnswerEvaluator(AnswerEvaluator):

    def __init__(self, question_attempt: QuestionAttempt):
        super().__init__(question_attempt)

    def evaluate(self):
        logger.info(
            f"🔍 MCQAnswerEvaluator.evaluate() called for question attempt: {self.question_attempt.id}"
        )

        if self.question_attempt.status == QuestionAttempt.Status.EVALUATED:
            logger.info(f"🔍 Question attempt already evaluated")
            return

        logger.info(f"🔍 Question attempt status: {self.question_attempt.status}")

        eval_data = {
            "is_correct": self.question_attempt.question.question_data["answer"]
            == self.question_attempt.mcq_answer
        }
        logger.info(f"🔍 Eval data: {eval_data}")
        self.question_attempt.eval_data = eval_data
        self.question_attempt.status = QuestionAttempt.Status.EVALUATED

        self.question_attempt.save()
