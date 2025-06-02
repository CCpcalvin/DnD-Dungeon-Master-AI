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
class ItemUseResolutionResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> ItemUseResolutionResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return ItemUseResolutionResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                narrative=data["narrative"],
                health_change=data["health_change"],
                summary=data["summary"],
                is_item_consumed=data["is_item_consumed"],
                is_event_ended=data["is_event_ended"],
            )
        except Exception as e:
            return ItemUseResolutionResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class ItemUseResolutionResponseSuccess(ItemUseResolutionResponse):
    narrative: str
    health_change: int
    summary: str
    is_item_consumed: bool
    is_event_ended: bool


@dataclass
class ItemUseResolutionResponseError(ItemUseResolutionResponse):
    pass


class ItemUseResolutionRequest(LLMRequest):
    prompt_file = "item_use_resolution.txt"

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
                        "is_item_consumed": {"type": "boolean"},
                        "is_event_ended": {"type": "boolean"},
                    },
                    "required": [
                        "narrative",
                        "health_change",
                        "summary",
                        "is_item_consumed",
                        "is_event_ended",
                    ],
                },
            }
        )

    def update_user_prompt(
        self,
        player_action: str,
        item_to_use: Item,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                player_action=player_action,
                item_to_use=item_to_use.to_prompt(),
            )
        )

    def send(
        self,
        user_input: str,
        item_to_use: Item,
    ) -> ItemUseResolutionResponse:
        """Send the story extension request to the LLM."""
        self.update_user_prompt(
            player_action=user_input,
            item_to_use=item_to_use,
        )

        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=400,
            temperature=0.8,
        )

        return ItemUseResolutionResponse.process_response(ai_response)
