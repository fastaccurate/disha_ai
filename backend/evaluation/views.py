import logging
import importlib
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


from .repositories import (
    AssessmentAttemptRepository,
)
from .usecases import (
    AssessmentUseCase,
    EvaluationUseCase,
    AssessmentExpiredException,
    AssessmentReportUsecase,
)
from .models import AssessmentAttempt

module_name = "evaluation.assessment.assessment_classes"
module = importlib.import_module(module_name)


class FetchAssessmentConfigs(APIView):
    def get(self, request, format=None):
        assessment_configs = AssessmentUseCase.get_assessment_configs()
        return Response({"data": assessment_configs}, status=status.HTTP_200_OK)


class CreateAssessment(APIView):

    def post(self, request, format=None):

        data = request.data
        assessment_generation_id = data.get("assessment_generation_id")

        if not assessment_generation_id:
            return Response(
                {"error": "Assessment Generation ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            generated_assessment_data = AssessmentUseCase.create_new_assessment(
                assessment_generation_id
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response({"data": generated_assessment_data}, status=status.HTTP_200_OK)


class FetchQuestions(APIView):

    def get(self, request, format=None):
        assessment_id = request.query_params.get("assessment_id")
        question_id = int(request.query_params.get("question_id"))

        try:
            assessment = AssessmentUseCase.fetch_assessment_data_and_assert_validity(
                assessment_id
            )
        except AssessmentExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        if not assessment:
            return Response(
                {"error": "Invalid assessment_attempt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment_question_check = (
            AssessmentUseCase.check_if_question_exists_in_assessment_attempt(
                assessment_id, question_id
            )
        )
        if not assessment_question_check:
            return Response(
                {"error": "Question not in assessment"},
                status=status.HTTP_404_NOT_FOUND,
            )

        question_data = AssessmentUseCase.get_question_data(question_id, assessment)
        if not question_data:
            return Response(
                {"error": "Invalid question id"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"data": question_data}, status=status.HTTP_200_OK)


class FetchAssessmentHistory(APIView):

    def get(self, request, format=None):

        assessment_history = AssessmentUseCase.fetch_history_data()

        return Response({"data": assessment_history}, status=status.HTTP_200_OK)


class FetchAssessmentState(APIView):

    def get(self, request, format=None):
        assessment_id = request.query_params.get("assessment_id")

        assessment_state = AssessmentAttemptRepository.get_assessment_state(
            assessment_id
        )
        if not assessment_state:
            return Response(
                {"error": "Invalid assessment_attempt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"data": assessment_state}, status=status.HTTP_200_OK)


class FetchIndividualScorecard(APIView):

    def get(self, request, format=None):
        assessment_id = request.query_params.get("assessment_id")

        if not assessment_id:
            return Response(
                {"error": "Assessment ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scorecard = AssessmentUseCase.fetch_assessment_scorecard_by_id(
                assessment_id
            )
        except AssessmentAttempt.DoesNotExist:
            return Response(
                {"error": "Assessment attempt not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"data": scorecard}, status=status.HTTP_200_OK)


class SubmitAssessmentAnswerMCQ(APIView):

    def post(self, request, format=None):
        data = request.data

        question_id = data.get("question_id")
        mcq_answer = data.get("mcq_answer")
        assessment_id = data.get("assessment_id")
        section = data.get("section")

        try:
            EvaluationUseCase.save_question_attempt(
                assessment_id, question_id, section, "mcq_answer", mcq_answer
            )
        except AssessmentExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        return Response({"data": "Answer submitted"}, status=status.HTTP_200_OK)


class SubmitAssessmentAnswerMMCQ(APIView):

    def post(self, request, format=None):

        data = request.data

        question_id = data.get("question_id")
        multiple_mcq_answer = data.get("multiple_mcq_answer")
        assessment_id = data.get("assessment_id")
        section = data.get("section")

        try:
            EvaluationUseCase.save_question_attempt(
                assessment_id,
                question_id,
                section,
                "multiple_mcq_answer",
                multiple_mcq_answer,
            )
        except AssessmentExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        return Response({"data": "Answer submitted"}, status=status.HTTP_200_OK)


class SubmitAssessmentAnswerSubjective(APIView):

    def post(self, request, format=None):

        data = request.data

        question_id = data.get("question_id")
        answer_text = data.get("answer_text")
        assessment_id = data.get("assessment_id")
        section = data.get("section")

        try:
            EvaluationUseCase.save_question_attempt(
                assessment_id, question_id, section, "answer_text", answer_text
            )
        except AssessmentExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        return Response({"data": "Answer submitted"}, status=status.HTTP_200_OK)


class SubmitAssessmentAnswerVoice(APIView):

    def post(self, request, format=None):

        data = request.data

        question_id = data.get("question_id")
        assessment_id = data.get("assessment_id")
        section = data.get("section")

        try:
            EvaluationUseCase.save_question_attempt(
                assessment_id, question_id, section, "voice"
            )
        except AssessmentExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        return Response({"data": "Answer submitted"}, status=status.HTTP_200_OK)


class CloseAssessment(APIView):

    def post(self, request, format=None):
        data = request.data

        assessment_id = data.get("assessment_id")

        if not assessment_id:
            return Response(
                {"error": "Assessment ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = AssessmentUseCase.fetch_assessment_data_and_assert_validity(
            assessment_id
        )
        if not assessment:
            return Response(
                {"error": "Invalid assessment_attempt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            logger.info(f"Starting evaluation for assessment {assessment_id})")
            EvaluationUseCase.evaluate_all_questions(assessment)

            # Refresh the assessment from database to get updated status
            assessment.refresh_from_db()
            logger.info(f"Assessment status after evaluation: {assessment.status}")

        except ValueError as e:
            # Handle LSRW validation error
            logger.error(
                f"LSRW validation error for assessment {assessment_id}: {str(e)}"
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Error during evaluation for assessment {assessment_id}: {str(e)}"
            )
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"error": "Failed to evaluate assessment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"data": "Assessment completed"}, status=status.HTTP_200_OK)


class FetchReport(APIView):

    def get(self, request):
        assessment_id = request.query_params.get("assessmentId")

        if not assessment_id:
            return Response(
                {"error": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = AssessmentReportUsecase.get_assessment_report(None, assessment_id)
        return Response({"data": data}, status=status.HTTP_200_OK)
