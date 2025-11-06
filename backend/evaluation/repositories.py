import logging

from .models import (
    Question,
    QuestionAttempt,
    AssessmentAttempt,
    AssessmentGenerationConfig,
    EventFlow,
)

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError


logger = logging.getLogger(__name__)


class QuestionRepository:

    def fetch_question(question_id):
        question = Question.objects.filter(id=question_id).first()
        return question

    def fetch_questions_by_ids(question_ids):
        questions = Question.objects.filter(id__in=question_ids)
        return questions


class AssessmentGenerationConfigRepository:

    def return_assessment_generation_class_data(assessment_generation_id):
        assessment_data = AssessmentGenerationConfig.objects.get(
            assessment_generation_id=assessment_generation_id
        )
        return assessment_data

    def get_assessment_generation_configs():
        assessment_data = AssessmentGenerationConfig.objects.all()
        return assessment_data


class AssessmentAttemptRepository:

    @staticmethod
    def fetch_assessment_from_report_id(report_id):
        assessment = AssessmentAttempt.objects.filter(report_id=report_id).first()
        return assessment

    def fetch_assessment_attempt(assessment_id):
        assessment = AssessmentAttempt.objects.get(assessment_id=assessment_id)
        return assessment

    def fetch_assessment_configs():
        assessments_available = AssessmentGenerationConfig.objects.filter(enabled=True)
        return assessments_available

    def get_assessment_state(assessment_id):
        assessment_attempt = AssessmentAttempt.objects.filter(
            assessment_id=assessment_id
        ).first()
        if not assessment_attempt:
            raise ValidationError("Assessment not found")

        if assessment_attempt.start_time is None:
            start_time = timezone.now()
            assessment_attempt.start_time = start_time
            assessment_attempt.save()

        question_list = assessment_attempt.question_list
        attempted_questions = QuestionAttemptRepository.fetch_attempted_questions(
            assessment_attempt
        )

        time_left = (
            assessment_attempt.start_time
            + assessment_attempt.test_duration
            - timezone.now()
        ).total_seconds()
        attempted_questions_data = []

        for attempt in attempted_questions:
            section = attempt.section
            mcq_answer = attempt.mcq_answer
            multiple_mcq_answer = attempt.multiple_mcq_answer
            answer_text = attempt.answer_text
            question_id = attempt.question_id
            attempted_questions_data.append(
                {
                    "question_id": question_id,
                    "section": section,
                    "mcq_answer": mcq_answer,
                    "multiple_mcq_answer": multiple_mcq_answer,
                    "answer_text": answer_text,
                }
            )

        assessment_status_resp = {
            "question_list": question_list,
            "attempted_questions": attempted_questions_data,
            "time_left": time_left if time_left > 0 else 0,
            "start_time": assessment_attempt.start_time,
            "test_duration": assessment_attempt.test_duration,
        }

        return assessment_status_resp

    def fetch_user_assessment_history():
        fields = [
            f.name for f in AssessmentAttempt._meta.fields
        ]  # Get all model fields
        fields.append(
            "assessment_generation_config_id__assessment_display_name"
        )  # Add the related field

        assessment_history = (
            AssessmentAttempt.objects.all()
            .filter(
                status__in=[
                    AssessmentAttempt.Status.ABANDONED,
                    AssessmentAttempt.Status.EVALUATION_PENDING,
                    AssessmentAttempt.Status.COMPLETED,
                ]
            )
            .select_related("assessment_generation_config_id")
            .order_by("-start_time")
            .values(*fields)
            .all()
        )
        return assessment_history

    def get_assessment_data(assessment_id):
        assessment_details = AssessmentAttempt.objects.filter(
            assessment_id=assessment_id
        ).first()
        return assessment_details

    def create_or_update_assessment_attempt(
        assessment_attempt=None,
        assessment_generation_id=None,
        status=None,
        question_list=None,
        last_saved=None,
        add_to_attempted_list=None,
        closed=None,
        test_duration=None,
        start_time=None,
        assessment_url=None,
        report_id=None,
        eval_data=None,
        evaluation_triggered=None,
        mode=None,
    ):
        if not assessment_attempt:
            assessment_attempt = AssessmentAttempt.objects.create(
                assessment_generation_config_id=assessment_generation_id,
                status=AssessmentAttempt.Status.IN_PROGRESS,
                test_duration=test_duration,
            )

        if assessment_url is not None:
            assessment_attempt.assessment_url = assessment_url
        if report_id is not None:
            assessment_attempt.report_id = report_id

        if status is not None:
            assessment_attempt.status = status
        if question_list is not None:
            assessment_attempt.question_list = question_list
        if last_saved is not None:
            assessment_attempt.last_saved = last_saved
        if add_to_attempted_list is not None:
            assessment_attempt.attempted_list.append(add_to_attempted_list)
        if closed is not None:
            assessment_attempt.closed = closed
        if test_duration is not None:
            assessment_attempt.test_duration = test_duration
        if start_time is not None:
            assessment_attempt.start_time = start_time
        if eval_data is not None:
            assessment_attempt.eval_data = eval_data
        if evaluation_triggered is not None:
            assessment_attempt.evaluation_triggered = evaluation_triggered
        if mode is not None:
            assessment_attempt.mode = mode
        assessment_attempt.save()

        return assessment_attempt.assessment_id


class QuestionAttemptRepository:

    def fetch_attempted_questions(assessment_attempt):
        attempted_questions = QuestionAttempt.objects.filter(
            assessment_attempt_id=assessment_attempt.assessment_id,
            status__in=[
                QuestionAttempt.Status.ATTEMPTED,
                QuestionAttempt.Status.EVALUATING,
            ],
        ).all()
        return attempted_questions

    def fetch_evaluated_questions(assessment_attempt):
        attempted_questions = QuestionAttempt.objects.filter(
            assessment_attempt_id=assessment_attempt.assessment_id,
            status__in=[QuestionAttempt.Status.EVALUATED],
        ).all()
        return attempted_questions

    def create_user_question_attempt(question_id, assessment_attempt_id):
        user_attempt, _ = QuestionAttempt.objects.get_or_create(
            question_id=question_id,
            assessment_attempt_id=assessment_attempt_id,
        )
        return user_attempt

    def save_user_question_attempt(
        user_question_attempt,
        mcq_answer=None,
        multiple_mcq_answer=None,
        answer_text=None,
        answer_audio_url=None,
        code=None,
        code_stubs=None,
        section=None,
        status=None,
    ):
        if multiple_mcq_answer is not None:
            user_question_attempt.multiple_mcq_answer = multiple_mcq_answer
        if mcq_answer is not None:
            user_question_attempt.mcq_answer = mcq_answer
        if status is not None:
            user_question_attempt.status = status
        if answer_text is not None:
            user_question_attempt.answer_text = answer_text
        if section is not None:
            user_question_attempt.section = section
        if answer_audio_url is not None:
            user_question_attempt.answer_audio_url = answer_audio_url
        if code is not None:
            user_question_attempt.code = code
        if code_stubs is not None:
            user_question_attempt.code_stubs = code_stubs
        user_question_attempt.save()

    def fetch_user_question_attempt(question_id, assessment_attempt):
        user_attempt = QuestionAttempt.objects.filter(
            question_id=question_id,
            assessment_attempt_id=assessment_attempt.assessment_id,
        ).first()
        return user_attempt

    def fetch_user_question_attempt_from_id(
        user, user_question_attempt_id, assessment_attempt
    ):
        user_attempt = QuestionAttempt.objects.filter(
            user_id=user.id,
            id=user_question_attempt_id,
            assessment_attempt_id=assessment_attempt.assessment_id,
        ).first()
        return user_attempt
