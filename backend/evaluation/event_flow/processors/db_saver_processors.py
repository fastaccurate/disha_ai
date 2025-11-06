from .base_event_processor import EventProcessor
from ...models import (
    AttemptResponseEvaluation,
    QuestionAttempt,
    AssessmentAttempt,
)
import logging

logger = logging.getLogger(__name__)


class BaseGrammarSaver(EventProcessor):

    def get_processor_name(self):
        raise NotImplemented

    def initialize(self):
        self.evaluation_id = self.root_arguments.get("evaluation_id")
        process_name = self.get_processor_name()
        self.grammar_score = self.inputs[process_name]["score"]
        self.grammar_details = self.inputs[process_name]

    def _execute(self):
        self.initialize()
        eval_object = AttemptResponseEvaluation.objects.get(id=self.evaluation_id)
        eval_object.grammar = self.grammar_score
        eval_object.grammar_details = self.grammar_details
        eval_object.save()
        return {}


class IELTSGrammarSaver(BaseGrammarSaver):

    def get_processor_name(self):
        return "Grammar"


class InterviewPrepGrammarSaver(BaseGrammarSaver):

    def get_processor_name(self):
        return "InterviewPrepGrammar"


class VocabSaver(EventProcessor):

    def initialize(self):
        self.evaluation_id = self.root_arguments.get("evaluation_id")
        self.vocab_score = self.inputs["Vocab"]["score"]
        self.vocab_details = self.inputs["Vocab"]

    def _execute(self):
        self.initialize()
        eval_object = AttemptResponseEvaluation.objects.get(id=self.evaluation_id)
        eval_object.vocab = self.vocab_score
        eval_object.vocab_details = self.vocab_details
        eval_object.save()
        return {}


class CoherenceSaver(EventProcessor):

    def initialize(self):
        self.evaluation_id = self.root_arguments.get("evaluation_id")
        self.coherence_score = self.inputs["Coherence"]["score"]
        self.coherence_details = self.inputs["Coherence"]

    def _execute(self):
        self.initialize()
        eval_object = AttemptResponseEvaluation.objects.get(id=self.evaluation_id)
        eval_object.coherence = self.coherence_score
        eval_object.coherence_details = self.coherence_details
        eval_object.save()
        return {}


class BaseEvaluationSaver(EventProcessor):

    def get_process_name(self):
        raise NotImplemented

    def initialize(self):
        self.evaluation_id = self.root_arguments.get("evaluation_id")
        process_name = self.get_process_name()
        self.final_score = self.inputs[process_name]["score"]
        self.summary = self.inputs[process_name]["summary"]
        self.score_title = self.inputs[process_name]["score_title"]

    def _execute(self):
        self.initialize()
        eval_object = AttemptResponseEvaluation.objects.get(id=self.evaluation_id)
        eval_object.summary = {
            "text": self.summary,
            "score": self.final_score,
            "overall_performance": self.score_title,
        }
        eval_object.score = self.final_score
        eval_object.status = AttemptResponseEvaluation.Status.COMPLETE
        eval_object.save()
        return {"summary": self.summary, "overall_score": self.final_score}


class WritingSaver(EventProcessor):
    def initialize(self):
        self.question_attemp_id = self.root_arguments.get("question_attempt_id")

        # Vocab is optional - only include if present in DAG
        self.vocab_details = self.inputs.get("Vocab", {})

        self.coherence_details = self.inputs["Coherence"]

        self.grammar_details = self.inputs["InterviewPrepGrammar"]

        self.final_score = self.inputs["WritingFinalScore"]["final_score"]
        self.grammar_score = self.inputs["WritingFinalScore"]["grammar"]
        self.vocab_score = self.inputs["WritingFinalScore"]["vocab"]
        self.coherence_score = self.inputs["WritingFinalScore"]["coherence"]

    def _execute(self):
        self.initialize()
        eval_object = QuestionAttempt.objects.get(id=self.question_attemp_id)

        eval_data = {
            "final_score": self.final_score,
            "vocab": {"score": self.vocab_score, "details": self.vocab_details},
            "coherence": {
                "score": self.coherence_score,
                "details": self.coherence_details,
            },
            "grammar": {"score": self.grammar_score, "details": self.grammar_details},
        }
        eval_object.eval_data = eval_data
        eval_object.status = QuestionAttempt.Status.EVALUATED

        eval_object.save()
        return {}
