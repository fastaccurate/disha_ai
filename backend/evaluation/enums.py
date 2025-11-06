"""
Enums for the evaluation app.
"""

from enum import Enum


class QuestionType(str, Enum):
    """
    Enum for different types of questions in the assessment system.
    """

    IELTS = "IELTS"
    INTERVIEW_PREP = "INTERVIEW_PREP"
    USER_CUSTOM_QUESTION = "USER_CUSTOM_QUESTION"
