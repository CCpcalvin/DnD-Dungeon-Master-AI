from __future__ import annotations

from game.classes.EntityClasses import Player
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponse

import json
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ItemIdentificationResponseModel(BaseModel):
    item_index: int = Field(
        ..., ge=0, description="Index of the identified item in the player's inventory"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the identification (0.0 to 1.0)",
    )


@dataclass
class ItemIdentificationResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> ItemIdentificationResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return ItemIdentificationResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                item_index=data["item_index"],
                confidence=data["confidence"],
            )
        except Exception as e:
            return ItemIdentificationResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class ItemIdentificationResponseSuccess(ItemIdentificationResponse):
    item_index: int
    confidence: float


@dataclass
class ItemIdentificationResponseError(ItemIdentificationResponse):
    pass


class ItemIdentificationRequest(LLMRequest):
    prompt_file = "item_identification.txt"

    def __init__(self, provider: LLMProvider, player: Player):
        super().__init__(provider)
        self.player = player

        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "item_index": {
                            "type": "integer",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                    },
                    "required": [
                        "item_index",
                        "confidence",
                    ],
                },
            }
        )

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

    def send(self) -> ItemIdentificationResponse:
        """
        Send the item identification request to the LLM.

        Returns:
            ItemIdentificationResponse: The identified item and confidence
        """
        self.update_user_prompt(user_input="")

        ai_response = self.provider.get_completion(
            response_model=ItemIdentificationResponseModel,
            messages=self.messages,
            max_tokens=100,
            temperature=0.1,
        )
        return ItemIdentificationResponse.process_response(ai_response)
