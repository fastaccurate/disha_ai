from evaluation.models import QuestionAttempt


class AnswerEvaluator:

    def __init__(self, question_attempt: QuestionAttempt):
        self.question_attempt = question_attempt

    def evaluate(self):
        raise NotImplementedError
