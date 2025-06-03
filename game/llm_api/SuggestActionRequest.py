from __future__ import annotations
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from game.classes.RollResults import RollResult
from game.models.LLMProvider import LLMProvider
from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

from game.llm_api.LLMRequest import LLMRequest, LLMResponse

import json
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List


class SuggestActionResponseModel(BaseModel):
    suggested_actions: List[str] = Field(
        ...,
        min_items=1,
        max_items=2,
        description="List of suggested actions for the player (1-2 items)",
    )


@dataclass
class SuggestActionResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> SuggestActionResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return SuggestActionResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                suggested_actions=data["suggested_actions"],
            )
        except Exception as e:
            return SuggestActionResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class SuggestActionResponseSuccess(SuggestActionResponse):
    suggested_actions: List[str] = None


@dataclass
class SuggestActionResponseError(SuggestActionResponse):
    pass


class SuggestActionRequest(LLMRequest):
    prompt_file = "suggest_action.txt"

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
                        "suggested_actions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                    "required": ["suggested_actions"],
                },
            }
        )

    def update_user_prompt(
        self,
        recent_history: str,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                recent_history=recent_history,
            )
        )

    def send(self) -> SuggestActionResponse:
        """
        Send the suggest action request to the LLM.

        Returns:
            SuggestActionResponse: The suggested actions for the player
        """
        self.update_user_prompt("")

        ai_response = self.provider.get_completion(
            response_model=SuggestActionResponseModel,
            messages=self.messages,
            max_tokens=200,
            temperature=0.7,
        )
        return SuggestActionResponse.process_response(ai_response)
