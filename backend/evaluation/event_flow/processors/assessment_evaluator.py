from evaluation.evaluators.AssessmentEvaluator import AssessmentEvaluator
from evaluation.event_flow.processors.base_event_processor import EventProcessor
from evaluation.models import AssessmentAttempt
import logging


logger = logging.getLogger(__name__)


class AssessmentEvaluatorProcessor(EventProcessor):
    def initialize(self):
        self.assessment_attempt_id = self.root_arguments.get("assessment_attempt_id")

    def _execute(self):
        self.log_info("🔍🔍🔍 AssessmentEvaluatorProcessor._execute() STARTED 🔍🔍🔍")
        self.initialize()
        assessment_attempt = AssessmentAttempt.objects.get(
            assessment_id=self.assessment_attempt_id
        )
        self.log_info(
            f"🔍🔍🔍 Found assessment_attempt {self.assessment_attempt_id} 🔍🔍🔍"
        )
        assessment_evaluator: AssessmentEvaluator = None

        assessment_evaluator = AssessmentEvaluator(assessment_attempt)

        self.log_info(
            f"🔍 About to call {type(assessment_evaluator).__name__}.evaluate()"
        )
        try:
            assessment_evaluator.evaluate()
            self.log_info(
                f"🔍 {type(assessment_evaluator).__name__}.evaluate() completed successfully"
            )
        except Exception as e:
            self.log_info(
                f"🔍 Error in {type(assessment_evaluator).__name__}.evaluate(): {str(e)}"
            )
            import traceback

            self.log_info(f"🔍 Traceback: {traceback.format_exc()}")
            raise
