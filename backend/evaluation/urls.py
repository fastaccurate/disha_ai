from django.urls import path
from .views import (
    CreateAssessment,
    FetchAssessmentConfigs,
    FetchQuestions,
    FetchIndividualScorecard,
    FetchAssessmentState,
    SubmitAssessmentAnswerMCQ,
    SubmitAssessmentAnswerMMCQ,
    SubmitAssessmentAnswerSubjective,
    SubmitAssessmentAnswerVoice,
    CloseAssessment,
    FetchReport,
    FetchAssessmentHistory,
)

urlpatterns = [
    path(
        "assessment-configs",
        FetchAssessmentConfigs.as_view(),
        name="assessment_configs",
    ),
    path("start-assessment", CreateAssessment.as_view(), name="start_assessment"),
    path("questions", FetchQuestions.as_view(), name="fetch_questions"),
    path(
        "assessment-state",
        FetchAssessmentState.as_view(),
        name="assessment_state",
    ),
    path(
        "submit-assessment-answer-mcq",
        SubmitAssessmentAnswerMCQ.as_view(),
        name="submit_assessment_answer_mcq",
    ),
    path(
        "submit-assessment-answer-mmcq",
        SubmitAssessmentAnswerMMCQ.as_view(),
        name="submit_assessment_answer_mmcq",
    ),
    path(
        "submit-assessment-answer-subjective",
        SubmitAssessmentAnswerSubjective.as_view(),
        name="submit_assessment_answer_subjective",
    ),
    path(
        "submit-assessment-answer-voice",
        SubmitAssessmentAnswerVoice.as_view(),
        name="submit_assessment_answer_voice",
    ),
    path("close-assessment", CloseAssessment.as_view(), name="close_assessment"),
    path(
        "assessment-history",
        FetchAssessmentHistory.as_view(),
        name="fetch_assessment_history",
    ),
    path(
        "fetch-individual-scorecard",
        FetchIndividualScorecard.as_view(),
        name="fetch_individual_scorecard",
    ),
    path("fetch-report", FetchReport.as_view(), name="fetch_report"),
    # Dedicated Public Assessment URLs - NO AUTHENTICATION REQUIRED
]
