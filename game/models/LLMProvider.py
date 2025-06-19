import os, json
import time
from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()

from typing import Type, TypeVar, Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def get_json_schema_response_format(self, response_model: BaseModel):
        response_format = response_model.model_json_schema()
        response_format["type"] = "json_object"
        return response_format

    @abstractmethod
    def get_completion(self, ResponseModel: Type[T], **kwargs) -> T:
        pass


class OpenAILikeProvider(LLMProvider):
    """OpenAI LLM"""

    max_retries = 3

    @abstractmethod
    def __init__(self):
        self.client: OpenAI
        pass

    def get_completion(
        self, ResponseModel: Type[T], model: str, verbose: bool = False, **kwargs
    ) -> T:
        for trial in range(self.max_retries):
            try:
                result = self.client.beta.chat.completions.parse(
                    model=model,
                    response_format=ResponseModel,
                    **kwargs,
                )

                if verbose:
                    print(result)

                if result.choices[0].message.content is None:
                    raise ValueError("No content in the response")

                return ResponseModel.model_validate_json(
                    result.choices[0].message.content
                )

            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                if trial != self.max_retries - 1:
                    print(f"Trial {trial + 1} failed. Retrying...")
                    time.sleep(1)
                    continue

                else:
                    raise e

            except Exception as e:
                raise e

        raise e


class ollama(OpenAILikeProvider):
    """Local LLM ollama"""

    max_retries = 3
    default_model = "llama3.1:8B"

    def __init__(self):
        self.client = OpenAI(base_url="http://ollama:11435/v1", api_key="ollama")

    def get_completion(
        self, ResponseModel: Type[T], model: str = default_model, **kwargs
    ) -> T:
        return super().get_completion(
            ResponseModel=ResponseModel, model=model, **kwargs
        )


class OpenRouterProvider(OpenAILikeProvider):
    #! TODO: Need to handle token limit, request limit, etc
    def __init__(self, model: Optional[str] = os.getenv("OPENROUTER_MODEL")):
        if model is None:
            raise ValueError("Model must be specified for OpenRouterProvider")

        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )


class MistralAIProvider(OpenRouterProvider):
    #! TODO: Mistral does not support structured output
    """
    In theory, faster than Llama 3.3 8B, but not that reliable
    ## Important!
        - The response format type cannot only be "text" and "json_object"
        - The structured output format is not supported
        - The response format does not work great too.
    """

    default_model = "mistralai/mistral-7b-instruct:free"


class Llama_3_3_8B_Instruct(OpenRouterProvider):
    """
    In theory, faster than Llama 3.3 8B, but not that reliable
    ## Important!
        - The response format does not work. I don't know why
        - Can only use structued output (which is actually nice)
    """

    default_model = "meta-llama/Llama-3.3-8B-Instruct:free"
