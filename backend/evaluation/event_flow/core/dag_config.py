DAG = {
    "writing": {
        "processors": {
            # "Vocab": {"depends_on": []},
            "InterviewPrepGrammar": {"depends_on": []},
            "Coherence": {"depends_on": []},
            "WritingFinalScore": {"depends_on": ["InterviewPrepGrammar", "Coherence"]},
            "WritingSaver": {
                "depends_on": ["InterviewPrepGrammar", "Coherence", "WritingFinalScore"]
            },
            "AssessmentEvaluatorProcessor": {"depends_on": ["WritingSaver"]},
        },
        "termination_processor": {"AbortHandler": {}},
    },
}
