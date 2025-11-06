import random
import logging
import openai
from OpenAIService.llm_classes.LLMConfig import GLOBAL_LOADED_LLM_CONFIGS, LLMConfig
from OpenAIService.models import (
    LLMConfigName,
    PromptTemplate,
)
from string import Template
from OpenAIService.openai_service import OpenAIService
from django.conf import settings


logger = logging.getLogger(__name__)


class ValidLLMConfigs:
    AzureOpenAILLMConfig = "AzureOpenAILLMConfig"

    @classmethod
    def get_all_valid_llm_configs(cls) -> list:
        return GLOBAL_LOADED_LLM_CONFIGS.keys()

    @classmethod
    def get_all_llm_configs_from_db(cls) -> list:
        return LLMConfigName.objects.all().values_list("name", flat=True)

    @classmethod
    def check_llm_configs_in_db(cls) -> bool:
        llm_configs_in_db = ValidLLMConfigs.get_all_llm_configs_from_db()
        loaded_configs = cls.get_all_valid_llm_configs()
        missing_config_names = [
            config_name
            for config_name in llm_configs_in_db
            if config_name not in loaded_configs
        ]
        if missing_config_names:
            raise ValueError(
                f"The following configs are missing from the configuration, but defined in DB: {missing_config_names} "
                f"To fix this, create these <name>.yaml files in {settings.LLM_CONFIGS_PATH} and restart the application."
            )
        return True


class ValidPromptTemplates:
    GRAMMAR_PROCESSOR = "grammar_processor"
    COHERENCE_PROCESSOR = "coherence_processor"

    @classmethod
    def get_all_valid_prompts(cls) -> list:
        return [
            cls.GRAMMAR_PROCESSOR,
            cls.COHERENCE_PROCESSOR,
        ]

    @classmethod
    def get_all_prompts_from_db(cls) -> list:
        return PromptTemplate.objects.all().values_list("name", flat=True)

    @classmethod
    def check_prompts_in_db(cls) -> bool:
        db_prompts = ValidPromptTemplates.get_all_prompts_from_db()
        code_prompts = cls.get_all_valid_prompts()
        missing_prompts = [
            prompt for prompt in code_prompts if prompt not in db_prompts
        ]
        if missing_prompts:
            raise ValueError(
                f"The following prompts are missing from the database: {missing_prompts}. "
                f"To fix this, set DISABLE_PROMPT_VALIDATIONS to True, start application and create these "
                f"prompt templates in DB."
            )
        return True


class PromptTemplateRepository:
    @staticmethod
    def get_by_name(name):
        try:
            prompt_template = PromptTemplate.objects.get(name=name)
            return prompt_template
        except PromptTemplate.DoesNotExist:
            return None


class LLMCommunicationWrapper:
    class LLMConfigsNotAvailable(Exception):
        def __init__(self) -> None:
            super().__init__("No LLM configs available.")

    @staticmethod
    def get_chat_history_init_msg_list(prompt_template, initializing_context_vars):
        if initializing_context_vars is None:
            initializing_context_vars = {}
        system_prompt = Template(prompt_template.system_prompt_template).substitute(
            initializing_context_vars
        )
        init_msg_list = [{"role": "system", "content": system_prompt}]
        for msg in prompt_template.initial_messages_templates:
            init_msg_list.append(
                {
                    "content": Template(msg["content"]).substitute(
                        initializing_context_vars
                    ),
                    "role": msg["role"],
                    "system_generated": True,
                    "show_in_user_history": False,
                }
            )
        return init_msg_list

    @staticmethod
    def get_response_without_chathistory(
        prompt_name,
        response_format_class=None,
        initializing_context_vars=None,
        retry_on_openai_time_limit=False,
    ):
        def select_llm_config(llm_config_names):
            random_llm_config_name = random.choice(llm_config_names)
            llm_config_instance: LLMConfig = GLOBAL_LOADED_LLM_CONFIGS[
                random_llm_config_name
            ]
            return llm_config_instance.get_config_dict(), random_llm_config_name

        prompt_template = PromptTemplate.objects.get(name=prompt_name)

        llm_config_names = [
            config.name for config in prompt_template.llm_config_names.all()
        ]
        if len(llm_config_names) == 0:
            raise LLMCommunicationWrapper.LLMConfigsNotAvailable()

        llm_config_params, llm_config_name = select_llm_config(llm_config_names)

        msg_list = LLMCommunicationWrapper.get_chat_history_init_msg_list(
            prompt_template, initializing_context_vars
        )

        while True:
            try:
                choice_response = OpenAIService.send_messages_and_get_response(
                    messages=msg_list,
                    llm_config_params=llm_config_params,
                    response_format_class=response_format_class,
                )
                break
            except openai._exceptions.RateLimitError as e:
                if retry_on_openai_time_limit:
                    llm_config_names.remove(llm_config_name)
                    llm_config_params, llm_config_name = select_llm_config(
                        llm_config_names
                    )
                else:
                    raise e

        response_msg_content = choice_response["message"]["content"]

        return response_msg_content
