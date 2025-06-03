from game.classes.LLMModel import LLMModel
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import json, os
from abc import ABC, abstractmethod
from dataclasses import dataclass


class LLMRequest(ABC):
    def __init__(self, model: LLMModel):
        self.model = model
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
    def send(self):
        pass

    def send_and_save(self, save_path: str, **kwargs):
        ai_response = self.send(**kwargs)

        to_save = {
            "input": kwargs,
            "messages": self.messages,
            "ai_response": ai_response.ai_response,
        }
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w") as f:
            json.dump(to_save, f)

        return ai_response


@dataclass
class LLMResponse:
    success: bool
    message: str
    ai_response: dict

    @abstractmethod
    @classmethod
    def process_response(cls, ai_response: dict):
        pass

    @classmethod
    def load_ai_response(cls, save_path: str) -> str:
        with open(save_path, "r") as f:
            raw_ai_response = json.load(f)

        return raw_ai_response["ai_response"]

    @classmethod
    def load(cls, save_path: str):
        ai_response = cls.load_ai_response(save_path)
        return cls.process_response(ai_response)
