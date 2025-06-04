from __future__ import annotations

from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest
from game.classes.NonCombatFloorType import NonCombatFloorType

from pydantic import BaseModel, Field
from typing import List


class NonCombatFloorIntroResponseModel(BaseModel):
    description: str = Field(
        ...,
        description="A detailed description of the floor's environment and atmosphere",
    )
    investigation_hook: str = Field(
        ...,
        description="A narrative hook to engage the player in investigating the floor",
    )
    suggested_actions: List[str] = Field(
        ...,
        min_items=1,
        max_items=2,
        description="List of suggested actions the player might take (1-2 items)",
    )
    summary: str = Field(..., description="A brief summary of the floor's key features")


class NonCombatFloorIntroRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "non_combat_floor_intro.txt"

    @property
    def ResponseModel(self):
        return NonCombatFloorIntroResponseModel

    def __init__(self, provider: LLMProvider, theme: str, player_description: str):
        super().__init__(provider)
        self.theme = theme
        self.player_description = player_description

    def update_user_prompt(self, floor_type: NonCombatFloorType):
        """Generate the user prompt by filling in the template with provided values."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player_description,
                floor_type=floor_type.value,
            )
        )

    def send(self, floor_type: NonCombatFloorType):
        """
        Send the non-combat floor intro request to the LLM.

        Args:
            floor_type: The type of non-combat floor

        Returns:
            NonCombatFloorIntroResponse: The generated floor introduction
        """
        self.update_user_prompt(floor_type)

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=400,
            temperature=0.8,
        )
