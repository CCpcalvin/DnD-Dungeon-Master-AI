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


class ItemUseResolutionResponseModel(BaseModel):
    narrative: str = Field(
        ..., description="A narrative description of the item use resolution"
    )
    health_change: int = Field(
        ...,
        ge=-10,
        le=10,
        description="The amount of health change from using the item (-10 to 10)",
    )
    summary: str = Field(..., description="A brief summary of the outcome")
    is_item_consumed: bool = Field(
        ..., description="Whether the item was consumed during use"
    )
    is_event_ended: bool = Field(
        ..., description="Whether the event is concluded after this item use"
    )


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
                        "narrative": {"type": "string"},
                        "health_change": {
                            "type": "integer",
                            "minimum": -10,
                            "maximum": 10,
                        },
                        "summary": {"type": "string"},
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
                    "additionalProperties": False,
                },
            }
        )

    def update_user_prompt(
        self,
        item_name: str,
        item_description: str,
        player_action: str,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                item_name=item_name,
                item_description=item_description,
                player_action=player_action,
            )
        )

    def send(
        self,
        item_name: str,
        item_description: str,
        player_action: str,
    ) -> ItemUseResolutionResponse:
        """
        Send the item use resolution request to the LLM.

        Args:
            item_name: The name of the item being used
            item_description: The description of the item
            player_action: The player's action description

        Returns:
            ItemUseResolutionResponse: The resolution of the item use
        """
        self.update_user_prompt(
            item_name=item_name,
            item_description=item_description,
            player_action=player_action,
        )

        ai_response = self.provider.get_completion(
            response_model=ItemUseResolutionResponseModel,
            messages=self.messages,
            max_tokens=400,
            temperature=0.8,
        )
        return ItemUseResolutionResponse.process_response(ai_response)
