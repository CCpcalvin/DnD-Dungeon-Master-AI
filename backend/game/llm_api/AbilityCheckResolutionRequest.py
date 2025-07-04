from __future__ import annotations

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.models.LLMProvider import LLMProvider

from game.classes.RollResults import RollResult
from game.classes.Progression import Progression

from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from pydantic import Field


class AbilityCheckResolutionResponseModel(LLMResponseModel):
    narrative: str = Field(
        ..., description="A narrative description of the check resolution"
    )
    health_change: int = Field(
        ...,
        ge=-9,
        le=9,
        description="The amount of health change from the check (-10 to 10)",
    )
    summary: str = Field(..., description="A brief summary of the outcome")


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
        progression: Progression,
        floor_type: NonCombatFloorType,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                floor_type=floor_type.value,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                player_action=player_action,
                roll_result=roll_result,
                progression=progression.to_prompt(),
            )
        )

    def send(
        self,
        player_action: str,
        roll_result: RollResult,
        progression: Progression,
        floor_type: NonCombatFloorType,
    ):
        """
        Send the request to the LLM and return the response.

        Args:
            player_action (str): The player's action description
            roll_result (RollResult): The result of the ability check roll

        Returns:
            AbilityCheckResolutionResponse: The response from the LLM
        """
        self.update_user_prompt(
            player_action=player_action,
            roll_result=roll_result,
            progression=progression,
            floor_type=floor_type,
        )

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=300,
            temperature=0.8,
        )
