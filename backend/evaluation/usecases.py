from rest_framework.exceptions import ValidationError

from .models import (
    AssessmentAttempt,
    QuestionAttempt,
    Question,
)
from evaluation.repositories import (
    AssessmentAttemptRepository,
    AssessmentGenerationConfigRepository,
    QuestionRepository,
    QuestionAttemptRepository,
)

from datetime import timedelta
from evaluation.evaluators.AssessmentEvaluator import AssessmentEvaluator

from .tasks import mark_test_abandoned

from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


import importlib


class AssessmentExpiredException(Exception):
    pass


class AssessmentUseCase:

    @staticmethod
    def get_assessment_configs():
        available_assessments = (
            AssessmentGenerationConfigRepository.get_assessment_generation_configs()
        )
        resp_data = []
        for assessment in available_assessments:
            assessment_generation_id = assessment.assessment_generation_id

            name = assessment.assessment_display_name

            resp_obj = {
                "assessment_generation_id": assessment_generation_id,
                "instructions": assessment.display_data.get("instructions"),
                "eval_home": {
                    "heading": f"{name}",
                },
                "name": name,
            }

            resp_data.append(resp_obj)
        resp_data.sort(key=lambda x: x["assessment_generation_id"])
        return resp_data

    def get_question_data(question_id, assessment):
        question = Question.objects.filter(id=question_id).first()
        resp_question_data = {
            "question_id": question.id,
            "answer_type": question.answer_type,
        }

        if question.question_data.get("questions"):
            questions = []
            for q in question.question_data.get("questions"):
                questions.append(
                    {
                        "question": q.get("question"),
                        "options": q.get("options"),
                    }
                )
            resp_question_data["questions"] = questions

        if question.question_data.get("paragraph"):
            resp_question_data["paragraph"] = question.question_data.get("paragraph")

        if question.question_data.get("question"):
            resp_question_data["question"] = question.question_data.get("question")

        if question.question_data.get("options"):
            resp_question_data["options"] = question.question_data.get("options")

        if question.question_data.get("hint"):
            resp_question_data["hint"] = question.question_data.get("hint")

        if question.question_data.get("image_url"):
            resp_question_data["image_url"] = question.question_data.get("image_url")

        if question.question_data.get("hints"):
            resp_question_data["hints"] = question.question_data.get("hints")

        if question.question_data.get("titleSlug"):
            resp_question_data["titleSlug"] = question.question_data.get("titleSlug")

        if question.question_data.get("questionTitle"):
            resp_question_data["questionTitle"] = question.question_data.get(
                "questionTitle"
            )

        if question.question_data.get("difficulty"):
            resp_question_data["difficulty"] = question.question_data.get("difficulty")
            difficulty = question.question_data.get("difficulty").lower()
            if difficulty == "basic":
                resp_question_data["expected_time"] = 20
            elif difficulty == "easy":
                resp_question_data["expected_time"] = 30
            elif difficulty == "medium":
                resp_question_data["expected_time"] = 45
            elif difficulty == "hard":
                resp_question_data["expected_time"] = 60

        resp_question_data["assessment_mode"] = assessment.mode

        return resp_question_data

    def assert_assessment_validity(start_time, test_duration, status):
        if not start_time:
            return
        expiration_time = start_time + test_duration
        buffer_duration_minutes = 2
        buffer_duration = timedelta(minutes=buffer_duration_minutes)

        if (
            status == int(AssessmentAttempt.Status.ABANDONED)
            or status == int(AssessmentAttempt.Status.COMPLETED)
            or status == int(AssessmentAttempt.Status.EVALUATION_PENDING)
        ):
            raise AssessmentExpiredException("Test has been abandoned or completed")
        if timezone.now() > expiration_time + buffer_duration:
            raise AssessmentExpiredException("Test time has expired")

    def fetch_assessment_data(assessment_id):
        assessment_details = AssessmentAttemptRepository.get_assessment_data(
            assessment_id=assessment_id
        )
        if not assessment_details:
            raise ValidationError("Assessment not found")

        return assessment_details

    def fetch_assessment_data_and_assert_validity(assessment_id):
        assessment_details = AssessmentUseCase.fetch_assessment_data(
            assessment_id=assessment_id
        )

        AssessmentUseCase.assert_assessment_validity(
            assessment_details.start_time,
            assessment_details.test_duration,
            assessment_details.status,
        )

        return assessment_details

    def check_if_question_exists_in_assessment_attempt(assessment_id, question_id):
        assessment = AssessmentUseCase.fetch_assessment_data_and_assert_validity(
            assessment_id
        )
        if assessment:
            for item in assessment.question_list:
                if question_id in item.get("questions"):
                    return True
        return False

    def create_new_assessment(assessment_generation_id):

        assessment_generation_class_data = AssessmentGenerationConfigRepository.return_assessment_generation_class_data(
            assessment_generation_id
        )
        kwargs = assessment_generation_class_data.kwargs
        class_name = assessment_generation_class_data.assessment_generation_class_name
        test_duration = assessment_generation_class_data.test_duration

        module_name = "evaluation.assessment.assessment_classes"

        try:
            module = importlib.import_module(module_name)
            assessment_class = getattr(module, class_name)
        except AttributeError as e:
            logger.error(f"Assessment class '{class_name}' not found in {module_name}")
            logger.error(f"Available classes: {dir(module)}")
            raise ValueError(
                f"Assessment class '{class_name}' not found. Available classes: {[cls for cls in dir(module) if not cls.startswith('_')]}"
            )
        except Exception as e:
            logger.error(f"Error importing assessment class '{class_name}': {str(e)}")
            raise ValueError(
                f"Failed to import assessment class '{class_name}': {str(e)}"
            )

        assessment_creation_instance = assessment_class(assessment_generation_id)

        generated_assessment_data = (
            assessment_creation_instance.generate_assessment_attempt()
        )

        assessment_id = AssessmentAttemptRepository.create_or_update_assessment_attempt(
            test_duration=test_duration,
            assessment_generation_id=assessment_generation_class_data,
            status=AssessmentAttempt.Status.IN_PROGRESS,
            question_list=generated_assessment_data["questions"],
        )

        generated_assessment_data["assessment_id"] = assessment_id

        buffer_duration_minutes = 2
        buffer_duration = timedelta(minutes=buffer_duration_minutes)
        total_delay = test_duration + buffer_duration
        total_delay_seconds = total_delay.total_seconds()
        mark_test_abandoned.apply_async(
            args=[assessment_id], countdown=total_delay_seconds
        )

        return generated_assessment_data

    def fetch_assessment_scorecard_by_id(assessment_id):
        assessment = AssessmentAttemptRepository.fetch_assessment_attempt(assessment_id)
        scorecard = AssessmentUseCase.fetch_assessment_scorecard(assessment)
        return scorecard

    def fetch_assessment_scorecard(assessment: AssessmentAttempt):
        mode = assessment.mode
        heading = ""
        for choice in AssessmentAttempt.Mode.choices:
            if int(choice[0]) == int(mode):
                heading = choice[1]
                break
        evaluation_data = assessment.eval_data
        resp_data = {
            "heading": heading,
            "last_attempt": assessment.start_time,
            "mode": mode,
            "status": assessment.status,
        }
        if assessment.eval_data.get("percentage"):
            resp_data["percentage"] = assessment.eval_data.get("percentage")

        resp_data.update(evaluation_data)

        return resp_data

    def fetch_history_data():
        available_assessments = AssessmentAttemptRepository.fetch_assessment_configs()

        # Initialize response containers
        filter_options = []
        resp_data = []

        # Build filter options in one pass
        for assessment in available_assessments:

            filter_options.append(
                {
                    "name": assessment.assessment_display_name,
                    "shortForm": "".join(
                        word[0].upper()
                        for word in assessment.assessment_display_name.split()
                    ),
                }
            )

        # Fetch history with all needed fields in one query
        history = AssessmentAttemptRepository.fetch_user_assessment_history()

        # Process history items efficiently
        for item in history:
            eval_data = item.get("eval_data", {})
            max_score = eval_data.get("max_score")
            total_score = eval_data.get("total_score")

            # Determine assessment type from assessment configuration
            assessment_type = "Objective"  # Default

            # Build response object
            resp_data.append(
                {
                    "last_attempted": item.get("start_time"),
                    "assessment_id": item.get("assessment_id"),
                    "type": item.get("type"),
                    "status": item.get("status"),
                    "percentage": f"{eval_data.get('percentage')}%",
                    "short_description": eval_data.get("short_description"),
                    "total_obtained": total_score,
                    "grand_total": max_score,
                    "assessment_name": item.get(
                        "assessment_generation_config_id__assessment_display_name"
                    ),
                    "assessment_config_id": item.get("assessment_generation_config_id"),
                    # Add assessment type for display
                    "assessment_type": assessment_type,
                }
            )

        return {"filter_options": filter_options, "attempted_list": resp_data}


class EvaluationUseCase:

    def save_question_attempt(
        assessment_id, question_id, section, answer_type=None, answer=None
    ):

        assessment_attempt = (
            AssessmentUseCase.fetch_assessment_data_and_assert_validity(assessment_id)
        )
        user_attempt = QuestionAttemptRepository.fetch_user_question_attempt(
            question_id, assessment_attempt
        )
        if not user_attempt:
            user_attempt = QuestionAttemptRepository.create_user_question_attempt(
                question_id, assessment_attempt
            )

        kwargs = {}
        if answer_type is not None and answer is not None:
            kwargs[answer_type] = answer
        QuestionAttemptRepository.save_user_question_attempt(
            user_attempt, status=QuestionAttempt.Status.ATTEMPTED, **kwargs
        )

        if section is not None:
            QuestionAttemptRepository.save_user_question_attempt(
                user_attempt, section=section
            )
            AssessmentAttemptRepository.create_or_update_assessment_attempt(
                assessment_attempt
            )

        if user_attempt.id not in assessment_attempt.attempted_list:
            AssessmentAttemptRepository.create_or_update_assessment_attempt(
                assessment_attempt,
                last_saved=question_id,
                add_to_attempted_list=user_attempt.id,
            )

        return

    def evaluate_all_questions(assessment):
        logger.info(
            f"🔍🔍🔍 evaluate_all_questions STARTED for assessment {assessment.assessment_id} 🔍🔍🔍"
        )
        logger.info(f"🔍🔍🔍 Assessment status: {assessment.status} 🔍🔍🔍")

        AssessmentAttemptRepository.create_or_update_assessment_attempt(
            assessment, closed=True, status=AssessmentAttempt.Status.EVALUATION_PENDING
        )

        # Check if this is an MCQ assessment first to decide evaluation strategy
        assessment_config = assessment.assessment_generation_config_id

        logger.info(f"🔍 Evaluating assessment: {assessment.assessment_id}")
        logger.info(
            f"   - Assessment config: {assessment_config.assessment_generation_id}"
        )

        evaluator_mapping = {
            "mcq_answer": "MCQAnswerEvaluator",
            "multiple_mcq_answer": "MultipleMCQAnswerEvaluator",
            "answer_text": "WritingAnswerEvaluator",
        }

        attempted_questions_list = QuestionAttemptRepository.fetch_attempted_questions(
            assessment
        )
        logger.info(
            f"   - Found {len(attempted_questions_list)} attempted questions for individual evaluation"
        )

        for user_attempt in attempted_questions_list:
            answer_type = None
            if user_attempt.mcq_answer is not None:
                answer_type = "mcq_answer"
            elif user_attempt.multiple_mcq_answer is not None:
                answer_type = "multiple_mcq_answer"
            elif user_attempt.answer_text is not None:
                answer_type = "answer_text"
            logger.info(
                f"🔍🔍🔍 Question {user_attempt.question_id}: answer_type={answer_type} 🔍🔍🔍"
            )
            evaluator_class_name = evaluator_mapping.get(answer_type)
            logger.info(f"🔍🔍🔍 Evaluator class name: {evaluator_class_name} 🔍🔍🔍")
            if evaluator_class_name:
                logger.info(
                    f"🔍🔍🔍 Using evaluator: {evaluator_class_name} for question {user_attempt.question_id} 🔍🔍🔍"
                )
                try:
                    evaluator_module = importlib.import_module(
                        f"evaluation.evaluators.{evaluator_class_name}"
                    )
                    evaluator = getattr(evaluator_module, evaluator_class_name)
                    evaluation_instance = evaluator(question_attempt=user_attempt)
                    logger.info(
                        f"🔍🔍🔍 About to call evaluator.evaluate() for question {user_attempt.question_id} 🔍🔍🔍"
                    )
                    evaluation_instance.evaluate()
                    logger.info(
                        f"🔍🔍🔍 evaluator function called for question {user_attempt.question_id} 🔍🔍🔍"
                    )
                except Exception as e:
                    logger.info(
                        f"   - Error evaluating question {user_attempt.question_id}: {str(e)}"
                    )
                    import traceback

                    logger.info(f"   - Traceback: {traceback.format_exc()}")
            else:
                logger.info(f"   - No evaluator found for answer_type: {answer_type}")

        assessment_evaluator: AssessmentEvaluator = AssessmentEvaluator(assessment)

        assessment_evaluator.evaluate()


class AssessmentReportUsecase:
    @staticmethod
    def get_assessment_report(user, assessment_id):
        assessment_attempt = AssessmentAttemptRepository.fetch_assessment_attempt(
            assessment_id
        )
        if not assessment_attempt:
            return None

        eval_data = assessment_attempt.eval_data
        if eval_data:
            eval_data["assessment_details"] = {
                "assessment_id": assessment_attempt.assessment_id,
                "assessment_name": assessment_attempt.assessment_generation_config_id.assessment_display_name,
            }

        report = {
            "status": assessment_attempt.status,
            "data": eval_data,
        }

        return report
