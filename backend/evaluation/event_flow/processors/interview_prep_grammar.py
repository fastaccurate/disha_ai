import logging
from evaluation.enums import QuestionType
from evaluation.event_flow.processors.base_grammar import BaseGrammar

logger = logging.getLogger(__name__)


class InterviewPrepGrammar(BaseGrammar):
    def __init__(self, *args, **kwargs):
        logger.info(f"🔍🔍🔍 InterviewPrepGrammar.initialize() STARTED 🔍🔍🔍")
        super().__init__(*args, **kwargs)
        self.question_type = QuestionType.INTERVIEW_PREP
        logger.info(f"🔍🔍🔍 InterviewPrepGrammar.initialize() COMPLETED 🔍🔍🔍")
