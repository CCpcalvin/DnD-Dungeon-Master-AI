from __future__ import annotations
from game.models.LLMProvider import LLMProvider
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import json, os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel
from typing import TypeVar, Any, Optional

T = TypeVar("T", bound="LLMResponseModel")


class LLMRequest(ABC):
    @property
    @abstractmethod
    def prompt_file(self) -> str:
        """The filename of the prompt template to use."""
        pass

    @property
    @abstractmethod
    def ResponseModel(self) -> type[LLMResponseModel]:
        """The response model class for this request."""
        pass

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": ""},
        ]

        self.response_format = {}
        self.load_system_prompt()
        self.load_user_prompt_template()

    def set_system_prompt(self, system_prompt: str):
        self.messages[0]["content"] = system_prompt

    def set_user_prompt(self, user_prompt: str):
        self.messages[1]["content"] = user_prompt

    def set_response_format(self, response_format: dict):
        self.response_format = response_format

    def load_system_prompt(self):
        with open(os.path.join(SYSTEM_PROMPT_PATH, self.prompt_file), "r") as f:
            self.set_system_prompt(f.read())

    def load_user_prompt_template(self):
        with open(os.path.join(USER_PROMPT_PATH, self.prompt_file), "r") as f:
            self.user_prompt_template = f.read()

    @abstractmethod
    def update_user_prompt(self, **kwargs):
        pass

    @abstractmethod
    def send(self) -> LLMResponseModel:
        pass

    def send_and_save(self, save_path: str, **kwargs) -> Any:
        """Send the request and save the response to a file."""
        response = self.send(**kwargs)

        with open(save_path, "w") as f:
            f.write(response.model_dump_json())

        return response

    def check_mock_exists(self, current_mock_dir: str, file_name: str) -> bool:
        """
        Check if the mock file exists.
        """
        file_path = os.path.join(current_mock_dir, file_name)
        return os.path.exists(file_path)

    def send_and_save_to_mock(
        self, mocks_dir: str, save_file_name: str, mock: Optional[int], **kwargs
    ):
        """
        Load the response from a mock file if mock is set, otherwise
        Send the request and save the response to a file in the mock directory.
        For testing purposes only.

        Args:
            mock_dir_path: The directory path to save the mock file.
            save_file_name: The name of the file to save the response as.
            mock: If set, load the response from a mock file.

        Returns:
            The response object from self.send().
        """
        if mock is not None:
            current_mock_dir = os.path.join(mocks_dir, f"{mock}")
            if self.check_mock_exists(current_mock_dir, save_file_name):
                # Load the mock response from a file
                response = self.ResponseModel.load(
                    os.path.join(current_mock_dir, save_file_name)
                )
            else:
                response = self.send_and_save(
                    save_path=os.path.join(current_mock_dir, save_file_name), **kwargs
                )

        else:
            response = self.send(**kwargs)

        return response


class LLMResponseModel(BaseModel):
    @classmethod
    def load(cls, save_path: str):
        """Load the response from a file."""
        with open(save_path, "r") as f:
            return cls.model_validate_json(f.read())
