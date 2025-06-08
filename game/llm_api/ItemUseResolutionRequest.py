from __future__ import annotations

from game.classes.ItemClasses import Item
from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.classes.NonCombatFloorType import NonCombatFloorType

from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from pydantic import Field


class ItemUseResolutionResponseModel(LLMResponseModel):
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


class ItemUseResolutionRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "item_use_resolution.txt"

    @property
    def ResponseModel(self):
        return ItemUseResolutionResponseModel

    def __init__(
        self, provider: LLMProvider, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

    def update_user_prompt(
        self, item_to_use: Item, user_input: str, floor_type: NonCombatFloorType
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                floor_type=floor_type.value,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                item_to_use=item_to_use.to_prompt(),
                player_action=user_input,
            )
        )

    def send(self, item_to_use: Item, user_input: str, floor_type: NonCombatFloorType):

        self.update_user_prompt(
            item_to_use=item_to_use,
            user_input=user_input,
            floor_type=floor_type,
        )
        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=400,
            temperature=0.8,
        )
