import abc
import logging
import traceback
import typing

from evaluation.models import EventFlow
import openai


from evaluation.event_flow.processors.expections import (
    CriticalProcessorException,
    ProcessorException,
)

logger = logging.getLogger(__name__)


class EventProcessor(abc.ABC):

    _logger = logger
    _fallback_result = {}

    def get_fallback_result(self):
        raise NotImplementedError

    def __init__(
        self, eventflow_id: str, inputs: typing.Dict, root_arguments: typing.Dict
    ):
        self.inputs = inputs
        self.root_arguments = root_arguments
        self.eventflow_id = eventflow_id

        # Add retry mechanism for EventFlow lookup with exponential backoff
        self.eventflow = self._get_eventflow_with_retry(eventflow_id)
        self.log_debug(f"Init function of processor called - {self.__class__.__name__}")

    def _get_eventflow_with_retry(
        self, eventflow_id: str, max_retries: int = 3, base_delay: float = 1.0
    ):
        """
        Get EventFlow with retry mechanism to handle race conditions.

        Args:
            eventflow_id: ID of the EventFlow to retrieve
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff

        Returns:
            EventFlow instance

        Raises:
            EventFlow.DoesNotExist: If EventFlow not found after all retries
        """
        import time

        for attempt in range(max_retries):
            try:
                eventflow = EventFlow.objects.get(id=eventflow_id)
                if attempt > 0:
                    logger.info(
                        f"EventFlow {eventflow_id} found on attempt {attempt + 1}"
                    )
                return eventflow
            except EventFlow.DoesNotExist:
                if attempt < max_retries - 1:  # Not the last attempt
                    delay = base_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"EventFlow {eventflow_id} not found (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {delay} seconds before retry..."
                    )
                    time.sleep(delay)
                else:
                    # Last attempt failed
                    logger.error(
                        f"EventFlow {eventflow_id} not found after {max_retries} attempts. "
                        f"This may indicate a race condition or system issue."
                    )
                    raise EventFlow.DoesNotExist(
                        f"EventFlow {eventflow_id} not found after {max_retries} retry attempts. "
                        f"Task may have been cleaned up or there's a system issue."
                    )

    def get_formatted_msg(self, msg):
        return f"ProcessorLog:[{self.eventflow_id}]:[{self.__class__.__name__}]:{msg}"

    def log_debug(self, msg):
        """Log debug message with processor name prefix."""
        self._logger.debug(self.get_formatted_msg(msg))

    def log_info(self, msg):
        """Log info message with processor name prefix."""
        self._logger.info(self.get_formatted_msg(msg))

    def log_warn(self, msg):
        """Log warning message with processor name prefix."""
        self._logger.warning(self.get_formatted_msg(msg))

    def log_warning(self, msg):
        """Alias for log_warn."""
        self.log_warn(msg)

    def log_error(self, msg):
        """Log error message with processor name prefix."""
        self._logger.error(self.get_formatted_msg(msg))

    def log_exception(self, msg):
        """Log exception message with processor name prefix and stack trace."""
        self._logger.exception(self.get_formatted_msg(msg))

    def execute(self):
        self.log_info(f"Execution starting.")
        try:
            results = self._execute()
        except CriticalProcessorException as cpe:
            self.log_exception(
                f"Processor {self.__class__.__name__} failed with error - {cpe.original_error_name}"
            )
            self.log_info(f"Processor-DONE -{self.__class__.__name__}-ERROR")

            stacktrace = cpe.original_error_stack_trace
            self.handle_critical_exception(stacktrace=stacktrace)
        except openai.RateLimitError as e:
            self.log_info(f"Processor got a retriable error - {e}")
            stacktrace = traceback.format_exc()
            self.submit_error(stacktrace, retriable=True)
            raise e
        except Exception as e:
            self.log_exception(f"Processor failed with error - {e}")
            self.log_info(f"Processor-DONE -{self.__class__.__name__}-ERROR")

            stacktrace = traceback.format_exc()
            self.submit_error(stacktrace, retriable=True)
        else:
            self.log_info(f"Processor-DONE -{self.__class__.__name__}")
            self.submit_result(results)

    @abc.abstractmethod
    def _execute(self) -> typing.Dict:
        pass

    def submit_error(self, stacktrace, retriable=False):
        from evaluation.event_flow.core.orchestrator import Orchestrator

        if retriable:
            Orchestrator(
                eventflow=self.eventflow, root_args=self.root_arguments
            ).submit_retriable_error(
                processor_name=self.__class__.__name__, stacktrace=stacktrace
            )
        else:
            Orchestrator(
                eventflow=self.eventflow, root_args=self.root_arguments
            ).submit_error(
                processor_name=self.__class__.__name__,
                stacktrace=stacktrace,
                abort_flow=True,
            )

    def submit_result(self, results: typing.Dict, error_stacktrace=None):
        from evaluation.event_flow.core.orchestrator import Orchestrator

        Orchestrator(
            eventflow=self.eventflow, root_args=self.root_arguments
        ).submit_result(
            processor_name=self.__class__.__name__,
            result_dict=results,
            error_stacktrace=error_stacktrace,
        )

    def handle_critical_exception(self, stacktrace):
        from evaluation.event_flow.core.orchestrator import Orchestrator

        Orchestrator(
            eventflow=self.eventflow, root_args=self.root_arguments
        ).submit_error(
            processor_name=self.__class__.__name__,
            stacktrace=stacktrace,
            abort_flow=True,
        )
