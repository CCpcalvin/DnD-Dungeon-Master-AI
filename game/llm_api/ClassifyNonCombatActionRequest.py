from __future__ import annotations

from game.classes.EntityClasses import Player
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from game.classes.FloorHistory import FloorHistory
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

from pydantic import BaseModel, Field
from typing import Literal


class ClassifyNonCombatActionResponseModel(LLMResponseModel):
    action_type: Literal["ability_check", "use_item", "go_to_next_floor", "unknown"] = (
        Field(
            ...,
            description="The type of action: 'ability_check', 'use_item', 'go_to_next_floor', or 'unknown'",
        )
    )
    narrative_consistency: bool = Field(
        ..., description="Whether the user input is consistent with the narrative"
    )


class ClassifyNonCombatActionRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "classify_non_combat_action.txt"

    @property
    def ResponseModel(self):
        return ClassifyNonCombatActionResponseModel

    def __init__(
        self,
        provider: LLMProvider,
        theme: str,
        player: Player,
        history: FloorHistory,
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

    def update_user_prompt(self, user_input: str):
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                player_inventory=self.player.inventory_prompt(),
                history=self.history.history_prompt(),
                user_input=user_input,
            )
        )

    def send(self, user_input: str):
        self.update_user_prompt(user_input)
        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=50,
            temperature=0.1,
        )
