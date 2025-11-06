import uuid
import typing

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

import datetime


class AttemptResponseEvaluation(models.Model):
    """
    This model is used to store the evaluations of the practice question.
    """

    class Status(models.IntegerChoices):
        PARTIAL = 1
        COMPLETE = 2
        ERROR = 3

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True, help_text=_("Unique ID")
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Cummulative score of evaluation"),
    )

    coherence = models.CharField(
        max_length=32, null=True, blank=True, help_text=_("Coherence score")
    )
    coherence_details = models.JSONField(
        null=True, blank=True, help_text=_("Additional coherence evaluation data")
    )

    grammar = models.CharField(
        max_length=32, null=True, blank=True, help_text=_("Grammar score")
    )
    grammar_details = models.JSONField(
        null=True, blank=True, help_text=_("Additional Grammar evaluation data")
    )

    summary = models.JSONField(
        null=True,
        blank=True,
        help_text=_("Any additional metadata related to the evaluation"),
    )

    status = models.IntegerField(choices=Status.choices, default=Status.PARTIAL)

    class Meta:
        verbose_name = _("Attempt Response Evaluation")
        verbose_name_plural = _("Attempt Response Evaluations")

    @cached_property
    def transscript_url(self):
        url = f"{self.id}/transcription_data/transcript.txt"
        return url

    @property
    def status_string(self):
        return self.Status(self.status).label


class EventFlow(models.Model):

    class Status(models.IntegerChoices):
        STARTED = 1
        COMPLETED = 2
        ERROR = 3
        ABORTED = 4

    TERMINATION_STATES = (Status.ERROR, Status.ABORTED)

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True, help_text=_("Unique ID")
    )

    type = models.CharField(max_length=24, null=False, blank=False)

    root_arguments = models.JSONField(
        null=True,
        blank=True,
        help_text=_("Arguments passed in while starting the event flow."),
    )
    status = models.IntegerField(choices=Status.choices, default=Status.STARTED)

    initiated_by = models.CharField(
        max_length=64, editable=False, help_text=_("Id of the initiator event/person")
    )

    run_duration = models.DurationField("Run duration", null=True, blank=True)

    start_time = models.DateTimeField(
        "Start time of event flow", null=True, blank=True, auto_now_add=True
    )

    end_time = models.DateTimeField("Start time of event flow", null=True, blank=True)

    @property
    def are_all_processors_complete(self):
        return not self.processors.exclude(
            status=EventFlowProcessorState.Status.COMPLETED
        )

    def check_if_given_processors_are_done(
        self, *, processor_names: typing.List[str]
    ) -> bool:
        return (
            not self.processors.exclude(
                status__in=EventFlowProcessorState.COMPLETION_STATES
            )
            .filter(processor_name__in=processor_names)
            .exists()
        )

    def get_summarized_status(self):
        processor_states = self.processors.distinct("processor_name").in_bulk(
            field_name="processor_name"
        )

        summarized_result = ""

        for processor_name, state in processor_states.items():
            status = state.get_status_display()
            summarized_result += f"{processor_name:25s}:{status}:{state.run_duration}\n"
        return summarized_result

    def get_processor_result(self, processor_name):
        return self.processors.get(processor_name=processor_name).result

    def get_processor_error(self, processor_name):
        return self.processors.get(processor_name=processor_name).error

    def save(self, *args, **kwargs):
        if self.pk:
            if self.processors.exists() and self.are_all_processors_complete:
                self.status = self.Status.COMPLETED
                self.end_time = timezone.now()
                if self.start_time:
                    self.run_duration = self.end_time - self.start_time
        super().save(*args, **kwargs)


class EventFlowProcessorState(models.Model):

    class Status(models.IntegerChoices):
        PENDING = 1
        IN_PROGRESS = 2
        COMPLETED = 3
        ERROR = 4
        COMPLETED_WITH_ERROR = 5
        ABORTED = 6
        RETRIABLE_ERROR = 7

    COMPLETION_STATES = (Status.COMPLETED, Status.COMPLETED_WITH_ERROR)

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True, help_text=_("Unique ID")
    )

    event_flow = models.ForeignKey(
        EventFlow, related_name="processors", on_delete=models.CASCADE
    )

    processor_name = models.CharField(max_length=32, help_text=_("Processor name"))

    result = models.JSONField(
        null=True, blank=True, help_text=_("All the result of the task.")
    )

    error = models.JSONField(
        null=True, blank=True, help_text=_("Error stack trace of the task")
    )

    retriable_error = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "Error stack trace of the task, only in case of a retriable error. Last error occurred will be stored."
        ),
    )

    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    run_duration = models.DurationField("Run duration", null=True, blank=True)

    start_time = models.DateTimeField("Start time of event flow", null=True, blank=True)

    end_time = models.DateTimeField("Start time of event flow", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event_flow", "processor_name"], name="unique_run"
            )
        ]


class Question(models.Model):

    class AnswerType(models.TextChoices):
        """
        Answer type signifies how the
        1. UI/UX should be for this question
        2. How evaluation should happen at a basic level.
        (Some details like prompt for evaluation might change based on other details of the question,
        but flow of evaluation will remain consistent for a particular answer type)
        3. Schema of question data.

        ANY OF THE ABOVE SHOULD ONLY BE DEPENDENT ON ANSWER TYPE AND AND NOT ON CATEGORY AND SUBCATEGORY.
        CATEGORY AND SUBCATEGORY ARE FOR THINGS LIKE FILTERING, ASSESSMENT CREATION ETC.
        """

        MCQ = (
            0,
            "MCQ",
        )
        MMCQ = (
            1,
            "MMCQ",
        )
        SUBJECTIVE = 2, "Subjective"

    id = models.AutoField(primary_key=True)
    answer_type = models.IntegerField(choices=AnswerType.choices, blank=True, null=True)
    question_data = models.JSONField(default=dict)
    """
    Schema for question_data
    {
        "tags": [],
        "question": "",
        "companies": [],
        "resources": {},
        "titleSlug": "",
        "difficulty": "",
        "questionTitle": "",
        "exampleTestcases": [],
        "additionalTestcases": []
    }"""
    markdown_question = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=1, blank=True, null=True)
    audio_url = models.URLField(max_length=500, blank=True, null=True)
    tags = models.JSONField(default=list)  # can be attention, processing-speed etc
    time_required = models.DurationField(default=datetime.timedelta(minutes=1))
    source = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class QuestionAttempt(models.Model):
    class Status(models.IntegerChoices):
        NOT_ATTEMPTED = 0, "Not Attempted"
        ATTEMPTED = 1, "Attempted"
        EVALUATING = 2, "Evaluating"
        EVALUATED = 3, "Evaluated"

    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    assessment_attempt_id = models.ForeignKey(
        "AssessmentAttempt",
        on_delete=models.DO_NOTHING,
        to_field="assessment_id",
        default=None,
    )
    section = models.CharField(
        max_length=255, blank=True, null=True
    )  # can be RC, Speaking, Reading, Writing
    mcq_answer = models.IntegerField(blank=True, null=True)
    multiple_mcq_answer = ArrayField(models.IntegerField(), blank=True, null=True)
    answer_text = models.TextField(blank=True, null=True)
    answer_audio_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_ATTEMPTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    eval_data = models.JSONField(default=dict, null=True)
    evaluation_id = models.UUIDField(editable=False, default=uuid.uuid4)
    """Schema for code_Stubs
            {
    "cpp": "",
    "java": "",
    "python": "",
    "javascript": ""
    }
    """

    class Meta:
        unique_together = ("question", "assessment_attempt_id")


class AssessmentAttempt(models.Model):
    class Status(models.TextChoices):
        CREATION_PENDING = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        COMPLETED = 2, "Completed"
        EVALUATION_PENDING = 3, "Evaluation Pending"
        ABANDONED = 4, "Abandoned"

    class Mode(models.TextChoices):
        EVALUATION = 0, "Evaluation"
        PRACTICE = 1, "Practice"

    assessment_id = models.AutoField(primary_key=True)
    assessment_generation_config_id = models.ForeignKey(
        "AssessmentGenerationConfig",
        on_delete=models.DO_NOTHING,
        to_field="assessment_generation_id",
    )
    attempted_list = models.JSONField(default=list)  # stores list of QuestionAttempt
    question_list = models.JSONField(default=list)  # stores list of all questions

    last_saved = models.CharField(max_length=255, blank=True, null=True)

    status = models.IntegerField(
        choices=Status.choices, default=Status.CREATION_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    evaluation_triggered = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    test_duration = models.DurationField()
    closed = models.BooleanField(
        default=False
    )  # set to True when the assessment is closed by the user (either in between or at the end)
    eval_data = models.JSONField(default=dict, null=True)
    assessment_url = models.TextField(blank=True, null=True)
    report_id = models.CharField(max_length=255, blank=True, null=True)
    mode = models.IntegerField(choices=Mode.choices, default=Mode.EVALUATION)


class AssessmentGenerationConfig(models.Model):
    enabled = models.BooleanField(default=True)
    assessment_generation_id = models.AutoField(primary_key=True)
    kwargs = models.JSONField(default=dict)
    assessment_generation_class_name = models.CharField(max_length=255)
    assessment_name = models.CharField(max_length=255, unique=True)
    assessment_display_name = models.CharField(max_length=255)
    test_duration = models.DurationField()
    display_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
