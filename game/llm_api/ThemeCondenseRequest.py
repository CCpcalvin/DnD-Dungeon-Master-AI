from __future__ import annotations
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.models.LLMProvider import LLMProvider
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import json
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ThemeCondenseResponseModel(BaseModel):
    theme: str = Field(
        ...,
        description="A 20 words or less description of the overall theme",
    )
    player_backstory: str = Field(
        ...,
        description="A 30 words or less description of the player's backstory",
    )


@dataclass
class ThemeCondenseResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> ThemeCondenseResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            return ThemeCondenseResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                theme=data.get("theme", ""),
                player_backstory=data.get("player_backstory", ""),
            )

        except Exception as e:
            return ThemeCondenseResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class ThemeCondenseResponseSuccess(ThemeCondenseResponse):
    theme: str
    player_backstory: str


@dataclass
class ThemeCondenseResponseError(ThemeCondenseResponse):
    pass


class ThemeCondenseRequest(LLMRequest):
    prompt_file = "theme_condense.txt"

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
                    },
                    "required": ["theme", "player_backstory"],
                },
            }
        )

    def update_user_prompt(self, theme: str, player_backstory: str):
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme, player_backstory=player_backstory
            )
        )

    def send(self, theme: str, player_backstory: str) -> ThemeCondenseResponse:
        """
        Send the theme condense request to the LLM.

        Args:
            theme: The original theme text
            player_backstory: The player's backstory

        Returns:
            ThemeCondenseResponse: The condensed theme and backstory
        """
        self.update_user_prompt(theme, player_backstory)

        ai_response = self.provider.get_completion(
            response_model=ThemeCondenseResponseModel,
            messages=self.messages,
            max_tokens=200,
            temperature=0.5,
        )
        return ThemeCondenseResponse.process_response(ai_response)
