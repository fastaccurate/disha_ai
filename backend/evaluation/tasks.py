import logging
import time

from celery import shared_task

from evaluation.event_flow.processors.base_event_processor import EventProcessor
from evaluation.event_flow.processors.assessment_evaluator import (
    AssessmentEvaluatorProcessor,
)
from evaluation.event_flow.processors.writing_final_score import WritingFinalScore
from evaluation.repositories import AssessmentAttemptRepository
from evaluation.models import AssessmentAttempt
import openai

from .celery import app

logger = logging.getLogger(__name__)


@shared_task
def add(*, x, y):
    return x + y


@shared_task(bind=True, max_retries=5, queue="evaluation_queue")
def call_event_processor(self, *, eventflow_id, processor_name, inputs, root_arguments):

    from evaluation.event_flow.processors.vocab import Vocab
    from evaluation.event_flow.processors.testingProcessor import TestingProcessor
    from evaluation.event_flow.processors.db_saver_processors import (
        CoherenceSaver,
        VocabSaver,
        IELTSGrammarSaver,
        InterviewPrepGrammarSaver,
        WritingSaver,
    )
    from evaluation.event_flow.processors.coherence import Coherence
    from evaluation.event_flow.processors.grammar import Grammar
    from evaluation.event_flow.processors.interview_prep_grammar import (
        InterviewPrepGrammar,
    )

    from evaluation.event_flow.processors.termination_processors import AbortHandler

    logger.info(f"🔍🔍🔍 call_event_processor() STARTED 🔍🔍🔍")
    logger.info(f"🔍🔍🔍 processor_name: {processor_name} 🔍🔍🔍")
    logger.info(f"🔍🔍🔍 inputs: {inputs} 🔍🔍🔍")
    logger.info(f"🔍🔍🔍 root_arguments: {root_arguments} 🔍🔍🔍")
    logger.info(f"Task {self.__dict__}")
    logger.info(f"🔍🔍🔍 Task {self.__dict__} 🔍🔍🔍")
    processors = [
        Coherence,
        Vocab,
        Grammar,
        InterviewPrepGrammar,
        CoherenceSaver,
        VocabSaver,
        IELTSGrammarSaver,
        InterviewPrepGrammarSaver,
        AbortHandler,
        WritingSaver,
        WritingFinalScore,
        AssessmentEvaluatorProcessor,
        TestingProcessor,
    ]

    processor_name_to_processors = {p.__name__: p for p in processors}
    processor_instance: EventProcessor = processor_name_to_processors[processor_name]
    try:
        logger.info(f"Celery calling processor class - {processor_instance}.")
        processor_instance(
            eventflow_id=eventflow_id, inputs=inputs, root_arguments=root_arguments
        ).execute()
    except openai.RateLimitError as exc:
        # Doing manual retry than celery decorator because that is showing
        default_retry_delay = 10
        max_retry_delay = 600
        retry_delay = min(
            default_retry_delay * (2**self.request.retries), max_retry_delay
        )
        # Log the retry status
        logger.info(
            f"{self.request.__dict__}, [{processor_name}-celery_task]: Retry #{self.request.retries + 1} in {retry_delay} seconds."
        )
        # Retry with calculated delay
        self.retry(exc=exc, countdown=retry_delay)


@shared_task(queue="evaluation_queue")
def mark_test_abandoned(assessment_id):
    try:
        assessment = AssessmentAttemptRepository.get_assessment_data(assessment_id)
        if not assessment:
            logger.error(f"Assessment with ID {assessment_id} does not exist.")
            return

        if assessment.status == int(AssessmentAttempt.Status.IN_PROGRESS):
            logger.info(f"Marking assessment with ID {assessment_id} as abandoned.")
            AssessmentAttemptRepository.create_or_update_assessment_attempt(
                assessment_attempt=assessment,
                closed=True,
                status=AssessmentAttempt.Status.ABANDONED,
            )

    except Exception as e:
        logger.exception(f"Error while marking test as abandoned: {e}")
