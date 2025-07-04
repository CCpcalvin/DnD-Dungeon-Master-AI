from __future__ import annotations

from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from game.classes.NonCombatFloorType import NonCombatFloorType

from pydantic import Field
from typing import List


class NonCombatFloorIntroResponseModel(LLMResponseModel):
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


class TreasureRoomIntroRequest(NonCombatFloorIntroRequest):
    @property
    def prompt_file(self):
        return "treasure_room_intro.txt"

    @classmethod
    def create_from_non_combat_floor_request(
        cls, non_combat_floor_request: NonCombatFloorIntroRequest
    ) -> TreasureRoomIntroRequest:
        """Create a TreasureRoomIntroRequest from a NonCombatFloorIntroRequest."""
        return cls(
            provider=non_combat_floor_request.provider,
            theme=non_combat_floor_request.theme,
            player_description=non_combat_floor_request.player_description,
        )


class TreasureRoomWithTrapIntroRequest(TreasureRoomIntroRequest):
    @property
    def prompt_file(self):
        return "treasure_room_with_trap_intro.txt"

class HiddenTrapRoomIntroRequest(TreasureRoomIntroRequest):
    @property
    def prompt_file(self):
        return "hidden_trap_room_intro.txt"

class NPCEncounterRoomIntroRequest(TreasureRoomIntroRequest):
    @property
    def prompt_file(self):
        return "npc_encounter_room_intro.txt"
