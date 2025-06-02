from __future__ import annotations

import json
from dataclasses import dataclass

from game.classes.EntityClasses import Player
from game.classes.LLMModel import LLMModel
from game.llm_api.LLMRequest import LLMRequest, LLMResponse


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

    def __init__(self, model: LLMModel, player: Player):
        super().__init__(model)
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

    def send(
        self,
        user_input: str,
    ) -> ItemIdentificationResponse:
        """Send the story extension request to the LLM."""
        self.update_user_prompt(
            user_input=user_input,
        )

        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=400,
            temperature=0.8,
        )

        return ItemIdentificationResponse.process_response(ai_response)
