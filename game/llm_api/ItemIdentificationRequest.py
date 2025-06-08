from __future__ import annotations

from game.classes.EntityClasses import Player
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel

from pydantic import Field


class ItemIdentificationResponseModel(LLMResponseModel):
    item_index: int = Field(
        ..., ge=0, description="Index of the identified item in the player's inventory"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the identification (0.0 to 1.0)",
    )


class ItemIdentificationRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "item_identification.txt"

    @property
    def ResponseModel(self):
        return ItemIdentificationResponseModel

    def __init__(self, provider: LLMProvider, player: Player):
        super().__init__(provider)
        self.player = player

    def update_user_prompt(
        self,
        user_input: str,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                user_input=user_input,
                # inventory_items=self.player.inventory_prompt(),
                inventory_items=self.player.inventory_full_prompt(),
            )
        )

    def send(self):
        """
        Send the item identification request to the LLM.

        Returns:
            ItemIdentificationResponse: The identified item and confidence
        """
        self.update_user_prompt(user_input="")

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=100,
            temperature=0.1,
        )
