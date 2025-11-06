from openai import AzureOpenAI
import time
from django.conf import settings
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.run import Run
import logging
import litellm
from pydantic import BaseModel


class OpenAIService:
    @staticmethod
    def _clean_schema_for_gemini(schema: dict) -> dict:
        """
        Remove additionalProperties from schema for Gemini compatibility.
        Gemini doesn't support the additionalProperties field in JSON schemas.
        """
        if isinstance(schema, dict):
            # Remove additionalProperties at current level
            schema.pop("additionalProperties", None)

            # Recursively clean nested schemas
            for key, value in schema.items():
                if isinstance(value, dict):
                    OpenAIService._clean_schema_for_gemini(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            OpenAIService._clean_schema_for_gemini(item)

        return schema

    @staticmethod
    def _is_gemini_model(model_name: str) -> bool:
        """Check if the model is a Gemini/Vertex AI model"""
        return model_name and ("gemini" in model_name.lower() or "vertex" in model_name.lower())

    @staticmethod
    def send_messages_and_get_response(
        messages: list,
        llm_config_params: dict,
        response_format_class: type[BaseModel] | None = None,
    ):
        # Check if we're using a Gemini model
        model_name = llm_config_params.get("model", "")
        is_gemini = OpenAIService._is_gemini_model(model_name)

        # For Gemini models with structured output, we need to clean the schema
        if is_gemini and response_format_class:
            # Get the JSON schema from the Pydantic model
            schema = response_format_class.model_json_schema()

            # Remove additionalProperties which Gemini doesn't support
            cleaned_schema = OpenAIService._clean_schema_for_gemini(schema)

            # Pass the cleaned schema directly
            response = litellm.completion(
                **llm_config_params,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_format_class.__name__,
                        "schema": cleaned_schema,
                        "strict": False
                    }
                }
            )
        else:
            # For non-Gemini models, use the standard approach
            response = litellm.completion(
                **llm_config_params,
                messages=messages,
                response_format=response_format_class,
            )

        return response["choices"][0]
