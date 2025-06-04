from __future__ import annotations

import json
import os
from dataclasses import dataclass

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.models.LLMProvider import LLMProvider
from game.classes.RollResults import RollResult
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from game.llm_api.LLMRequest import LLMRequest
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


class AbilityCheckResolutionRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "ability_check_resolution.txt"

    @property
    def ResponseModel(self):
        return AbilityCheckResolutionResponseModel

    def __init__(
        self, provider: LLMProvider, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

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

    def send(self, player_action: str, roll_result: RollResult):
        """
        Send the request to the LLM and return the response.

        Args:
            player_action (str): The player's action description
            roll_result (RollResult): The result of the ability check roll

        Returns:
            AbilityCheckResolutionResponse: The response from the LLM
        """
        self.update_user_prompt(player_action=player_action, roll_result=roll_result)

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=100,
            temperature=0.4,
        )
