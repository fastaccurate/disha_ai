from evaluation.event_flow.processors.base_event_processor import EventProcessor

class WritingFinalScore(EventProcessor):

    def initialize(self):
        self.coherence_score = str(self.inputs["Coherence"]["score"])
        self.grammar_score = int(self.inputs["InterviewPrepGrammar"]["score"])

        # Vocab is optional in the DAG - use default if not present
        vocab_input = self.inputs.get("Vocab", {"score": "B1"})
        self.vocab_score = str(vocab_input.get("score", "B1")).replace("+", "")

        self.coherence_completeness = str(self.inputs["Coherence"]["response"]["Completeness"])
        self.coherence_relevence = str(self.inputs["Coherence"]["response"]["Relevance"])
        self.coherence_logical = str(self.inputs["Coherence"]["response"]["Logical"])


    def _execute(self):
        self.initialize()
        vocab_score_to_number_mapping = {"": 0, "a1": 1, "a2": 3, "b1": 5, "b2": 7, "c1": 8.5, "c2": 9.5}

        coherence_completeness_to_number_mapping = {"yes": 2, "no": 1}
        coherence_relevance_to_number_mapping = {"high": 6, "medium": 3, "low": 1}
        coherence_logical_to_number_mapping = {"high": 2, "medium": 1, "low": 0}

        normalized_vocab_score = vocab_score_to_number_mapping.get(self.vocab_score.lower())*10

        # Handle None values from get() method by providing default values
        coherence_completeness_score = coherence_completeness_to_number_mapping.get(self.coherence_completeness.lower(), 0)
        coherence_relevance_score = coherence_relevance_to_number_mapping.get(self.coherence_relevence.lower(), 0)
        coherence_logical_score = coherence_logical_to_number_mapping.get(self.coherence_logical.lower(), 0)
        
        normalized_coherence_score = sum([
            coherence_completeness_score,
            coherence_relevance_score,
            coherence_logical_score
        ])*10
        
        normalized_grammar_score = round(self.grammar_score,2)*10

        final_score = round((
            int(normalized_grammar_score) +
            int(normalized_coherence_score) +
            int(normalized_vocab_score)
        ) / 6,1)

        return {"final_score": final_score, "grammar": normalized_grammar_score, "vocab": normalized_vocab_score, "coherence": normalized_coherence_score}
