from __future__ import annotations

import json
import os
from dataclasses import dataclass

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.models.LLMProvider import LLMProvider
from game.classes.RollResults import RollResult
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from pydantic import BaseModel, Field


class AbilityCheckResolutionResponseModel(BaseModel):
    narrative: str = Field(
        ..., description="A narrative description of the check resolution"
    )
    health_change: int = Field(
        ...,
        ge=-10,
        le=10,
        description="The amount of health change from the check (-10 to 10)",
    )
    summary: str = Field(..., description="A brief summary of the outcome")
    is_event_ended: bool = Field(
        ..., description="Whether the event is concluded after this check"
    )


@dataclass
class AbilityCheckResolutionResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> AbilityCheckResolutionResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return AbilityCheckResolutionResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                narrative=data["narrative"],
                health_change=data["health_change"],
                summary=data["summary"],
                is_event_ended=data["is_event_ended"],
            )
        except Exception as e:
            return AbilityCheckResolutionResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class AbilityCheckResolutionResponseSuccess(AbilityCheckResolutionResponse):
    narrative: str
    health_change: int
    summary: str
    is_event_ended: bool


@dataclass
class AbilityCheckResolutionResponseError(AbilityCheckResolutionResponse):
    pass


class AbilityCheckResolutionRequest(LLMRequest):
    prompt_file = "ability_check_resolution.txt"

    def __init__(
        self, provider: LLMProvider, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "narrative": {
                            "type": "string",
                        },
                        "health_change": {
                            "type": "integer",
                            "minimum": -10,
                            "maximum": 10,
                        },
                        "summary": {
                            "type": "string",
                        },
                        "is_event_ended": {"type": "boolean"},
                    },
                    "required": [
                        "narrative",
                        "health_change",
                        "summary",
                        "is_event_ended",
                    ],
                },
            }
        )

    def update_user_prompt(
        self,
        player_action: str,
        roll_result: RollResult,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                player_action=player_action,
                roll_result=roll_result,
            )
        )

    def send(
        self, player_roll: int, difficulty_class: int
    ) -> AbilityCheckResolutionResponse:
        """
        Send the request to the LLM and return the response.

        Args:
            player_roll: The player's roll result (1-20)
            difficulty_class: The difficulty class of the check

        Returns:
            AbilityCheckResolutionResponse: The response from the LLM
        """
        self.update_user_prompt(player_roll, difficulty_class)

        ai_response = self.provider.get_completion(
            response_model=AbilityCheckResolutionResponseModel,
            messages=self.messages,
            max_tokens=100,
            temperature=0.4,
        )
        return AbilityCheckResolutionResponse.process_response(ai_response)
