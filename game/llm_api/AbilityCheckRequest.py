from __future__ import annotations
from dataclasses import dataclass
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponse

from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import json
from typing import Literal
from pydantic import BaseModel, Field


class AbilityCheckResponseModel(BaseModel):
    attribute: Literal[
        "strength", "dexterity", "intelligence", "wisdom", "charisma"
    ] = Field(
        ...,
        description="The attribute to check. Must be one of: strength, dexterity, intelligence, wisdom, or charisma.",
    )
    difficulty_class: int = Field(
        ...,
        description="The difficulty class of the check.",
        ge=3,
        le=19,
    )


@dataclass
class AbilityCheckResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> AbilityCheckResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return AbilityCheckResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                attribute=data["attribute"],
                difficulty_class=data["difficulty_class"],
            )
        except Exception as e:
            return AbilityCheckResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class AbilityCheckResponseSuccess(AbilityCheckResponse):
    attribute: str
    difficulty_class: int


@dataclass
class AbilityCheckResponseError(AbilityCheckResponse):
    pass


class AbilityCheckRequest(LLMRequest):
    prompt_file = "ability_check.txt"

    def __init__(self, provider: LLMProvider, player: Player, history: FloorHistory):
        super().__init__(provider)

        self.player = player
        self.history = history

        # Set response format
        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "attribute": {
                            "type": "string",
                            "enum": [
                                "strength",
                                "dexterity",
                                "intelligence",
                                "wisdom",
                                "charisma",
                            ],
                        },
                        "difficulty_class": {
                            "type": "integer",
                            "minimum": 3,
                            "maximum": 19,
                        },
                    },
                    "required": [
                        "attribute",
                        "difficulty_class",
                    ],
                },
            }
        )

    def update_user_prompt(self, user_input: str):
        """Update the user prompt with the current action and player attributes."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                player_action=user_input,
                player_description=self.player.description,
                history=self.history.history_prompt(),
            )
        )

    def send(self, user_input: str) -> AbilityCheckResponse:
        self.update_user_prompt(user_input)

        """Send the request to the LLM and return the response."""
        ai_response = self.provider.get_completion(
            response_model=AbilityCheckResponseModel,
            messages=self.messages,
            max_tokens=50,
            temperature=0.4,
        )
        return AbilityCheckResponse.process_response(ai_response)
