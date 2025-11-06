from evaluation.enums import QuestionType


def get_eventflow_type_from_question_type(question_type):
    ef_type_map = {
        QuestionType.IELTS: "default",
        QuestionType.INTERVIEW_PREP: "interview_prep",
        QuestionType.USER_CUSTOM_QUESTION: "interview_prep",
    }
    return ef_type_map.get(question_type, "default")
