from __future__ import annotations
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.models.LLMProvider import LLMProvider
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import os, json
from dataclasses import dataclass
from pydantic import BaseModel, Field


class BackgroundResponseModel(BaseModel):
    theme: str = Field(..., description="The game's theme setting")
    player_backstory: str = Field(..., description="The player character's backstory")
    player_motivation: str = Field(..., description="The player character's motivation")


@dataclass
class BackgroundResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> BackgroundResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            return BackgroundResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                theme=data.get("theme", ""),
                player_backstory=data.get("player_backstory", ""),
                player_motivation=data.get("player_motivation", ""),
            )

        except Exception as e:
            return BackgroundResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class BackgroundResponseSuccess(BackgroundResponse):
    theme: str = ""
    player_backstory: str = ""
    player_motivation: str = ""


@dataclass
class BackgroundResponseError(BackgroundResponse):
    pass


class BackgroundRequest(LLMRequest):
    prompt_file = "background.txt"

    def __init__(self, provider: LLMProvider):
        super().__init__(provider)

        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "player_backstory": {"type": "string"},
                        "player_motivation": {"type": "string"},
                    },
                    "required": ["theme", "player_backstory", "player_motivation"],
                },
            }
        )

    def update_user_prompt(self):
        self.set_user_prompt(self.user_prompt_template)

    def send(self) -> BackgroundResponse:
        self.update_user_prompt()

        ai_response = self.provider.get_completion(
            response_model=BackgroundResponseModel,
            messages=self.messages,
            max_tokens=500,
            temperature=0.8,
        )
        return BackgroundResponse.process_response(ai_response)
