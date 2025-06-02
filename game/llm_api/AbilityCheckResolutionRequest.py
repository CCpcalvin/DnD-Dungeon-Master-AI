from __future__ import annotations

import json
import os
from dataclasses import dataclass

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.classes.LLMModel import LLMModel
from game.classes.RollResults import RollResult
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from game.llm_api.LLMRequest import LLMRequest, LLMResponse


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
        self, model: LLMModel, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(model)
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
        self,
        player_action: str,
        roll_result: RollResult,
    ) -> AbilityCheckResolutionResponse:
        """Send the story extension request to the LLM."""
        self.update_user_prompt(
            player_action=player_action,
            roll_result=roll_result,
        )

        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=400,
            temperature=0.8,
        )

        return AbilityCheckResolutionResponse.process_response(ai_response)
