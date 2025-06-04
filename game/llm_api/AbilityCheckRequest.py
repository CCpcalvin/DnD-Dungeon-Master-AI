from __future__ import annotations
from game.classes.EntityClasses import Player
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest

from typing import Literal
from pydantic import BaseModel, Field
from dataclasses import dataclass


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


class AbilityCheckRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "ability_check.txt"

    @property
    def ResponseModel(self):
        return AbilityCheckResponseModel

    def __init__(self, provider: LLMProvider, player: Player, history: FloorHistory):
        super().__init__(provider)

        self.player = player
        self.history = history

    def update_user_prompt(self, user_input: str):
        """Update the user prompt with the current action and player attributes."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                player_action=user_input,
                player_description=self.player.description,
                history=self.history.history_prompt(),
            )
        )

    def send(self, user_input: str):
        self.update_user_prompt(user_input)
        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=50,
            temperature=0.4,
        )
