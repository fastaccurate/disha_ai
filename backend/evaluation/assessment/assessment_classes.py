from ..repositories import AssessmentGenerationConfigRepository

import logging

logger = logging.getLogger(__name__)


class BaseAssessmentGenerationLogic:
    def __init__(self, assessment_generation_id):
        self.assessment_generation_id = assessment_generation_id
        self.assessment_config_data = AssessmentGenerationConfigRepository.return_assessment_generation_class_data(
            assessment_generation_id
        )
        self.kwargs = self.assessment_config_data.kwargs
        self.assessment_display_name = (
            self.assessment_config_data.assessment_display_name
        )

    def validate_kwargs(self):
        raise NotImplementedError(
            "validate_kwargs method must be implemented in subclasses"
        )

    def generate_assessment_attempt(self):
        raise NotImplementedError(
            "generate_assessment_attempt method must be implemented in subclasses"
        )


class QuestionIdsBasedAssessment(BaseAssessmentGenerationLogic):
    def __init__(self, assessment_generation_id):
        super().__init__(assessment_generation_id)

    def validate_kwargs(self):
        required_keys = ["total_number", "subcategories"]
        for key in required_keys:
            if key not in self.kwargs:
                return False, f"Missing required key: {key}"

        if not isinstance(self.kwargs["total_number"], int):
            return False, "'total_number' must be an integer"

        subcategories = self.kwargs["subcategories"]
        if not isinstance(subcategories, list):
            return False, "'subcategories' must be a list"

        for subcategory in subcategories:
            if (
                not isinstance(subcategory, dict)
                or "number" not in subcategory
                or "question_ids" not in subcategory
                or "skippable" not in subcategory
                or "section_name" not in subcategory
            ):
                return (
                    False,
                    "Each subcategory must be a dictionary with 'number', 'question_ids', 'section_name', and 'skippable' keys",
                )

            if not isinstance(subcategory["question_ids"], list):
                return False, "'question_ids' must be a list"

            if not all(isinstance(qid, int) for qid in subcategory["question_ids"]):
                return False, "All question IDs must be integers"

            if not isinstance(subcategory["skippable"], bool):
                return False, "'skippable' must be a boolean"

            if not isinstance(subcategory["number"], int):
                return False, "'number' in each subcategory must be an integer"

        return True, ""

    def generate_assessment_attempt(self):
        is_valid, message = self.validate_kwargs()
        if not is_valid:
            raise ValueError(message)

        # Format the question data to match the expected format
        formatted_questions = []
        for subcategory in self.kwargs["subcategories"]:
            formatted_questions.append(
                {
                    "section": subcategory["section_name"],
                    "questions": subcategory["question_ids"],
                    "skippable": subcategory["skippable"],
                }
            )

        return {
            "total_number": self.kwargs["total_number"],
            "questions": formatted_questions,
        }


class QuestionPoolBasedAssessment(BaseAssessmentGenerationLogic):
    def __init__(self, assessment_generation_id):
        super().__init__(assessment_generation_id)

    def validate_kwargs(self):
        required_keys = ["total_number", "subcategories"]
        for key in required_keys:
            if key not in self.kwargs:
                return False, f"Missing required key: {key}"

        if not isinstance(self.kwargs["total_number"], int):
            return False, "'total_number' must be an integer"

        subcategories = self.kwargs["subcategories"]
        if not isinstance(subcategories, list):
            return False, "'subcategories' must be a list"

        for subcategory in subcategories:
            if (
                not isinstance(subcategory, dict)
                or "number" not in subcategory
                or "question_pool" not in subcategory
                or "skippable" not in subcategory
                or "section_name" not in subcategory
            ):
                return (
                    False,
                    "Each subcategory must be a dictionary with 'number', 'question_pool', 'section_name', and 'skippable' keys",
                )

            if not isinstance(subcategory["question_pool"], list):
                return False, "'question_pool' must be a list"

            # Check if this is a custom MCQ assessment
            is_custom = subcategory.get("is_custom", False)

            # For both custom and regular questions, validate question IDs are positive integers
            if not all(
                isinstance(qid, int) and qid > 0 for qid in subcategory["question_pool"]
            ):
                return False, "All question IDs in pool must be positive integers"

            if not isinstance(subcategory["skippable"], bool):
                return False, "'skippable' must be a boolean"

            if not isinstance(subcategory["number"], int):
                return False, "'number' in each subcategory must be an integer"

            if subcategory["number"] > len(subcategory["question_pool"]):
                return (
                    False,
                    f"Requested number of questions ({subcategory['number']}) is greater than the pool size ({len(subcategory['question_pool'])})",
                )

        return True, ""

    def generate_assessment_attempt(self):
        import random

        is_valid, message = self.validate_kwargs()
        if not is_valid:
            raise ValueError(message)

        formatted_questions = []
        for subcategory in self.kwargs["subcategories"]:
            # Check if this is a custom MCQ assessment
            is_custom = subcategory.get("is_custom", False)

            if is_custom:
                # For custom MCQ assessments, use all questions in the pool
                selected_questions = subcategory["question_pool"]
            else:
                # For regular questions, randomly select the specified number from the pool
                selected_questions = random.sample(
                    subcategory["question_pool"], subcategory["number"]
                )

            formatted_questions.append(
                {
                    "section": subcategory["section_name"],
                    "questions": selected_questions,
                    "skippable": subcategory["skippable"],
                }
            )

        return {
            "total_number": self.kwargs["total_number"],
            "questions": formatted_questions,
        }
