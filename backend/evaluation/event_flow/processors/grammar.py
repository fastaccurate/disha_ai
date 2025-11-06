from evaluation.enums import QuestionType
from evaluation.event_flow.processors.base_grammar import BaseGrammar


class Grammar(BaseGrammar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.IELTS
