from __future__ import annotations
from dataclasses import dataclass
from game.classes.LLMModel import LLMModel
from game.llm_api.LLMRequest import LLMRequest, LLMResponse

from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
import os, json


@dataclass
class AbilityCheckResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> AbilityCheckResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])
            return AbilityCheckResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                attribute=data["attribute"],
                difficulty_class=data["difficulty_class"],
            )
        except Exception as e:
            return AbilityCheckResponseError(
                success=False, message=str(e), ai_response=ai_response
            )


@dataclass
class AbilityCheckResponseSuccess(AbilityCheckResponse):
    attribute: str = None
    difficulty_class: int = None


@dataclass
class AbilityCheckResponseError(AbilityCheckResponse):
    pass


class AbilityCheckRequest(LLMRequest):
    prompt_file = "ability_check.txt"

    def __init__(self, model: LLMModel, player: Player, history: FloorHistory):
        super().__init__(model)

        self.player = player
        self.history = history

        # Set response format
        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "attribute": {
                            "type": "string",
                            "enum": [
                                "strength",
                                "dexterity",
                                "intelligence",
                                "wisdom",
                                "charisma",
                            ],
                        },
                        "difficulty_class": {
                            "type": "integer",
                            "minimum": 3,
                            "maximum": 19,
                        },
                    },
                    "required": [
                        "attribute",
                        "difficulty_class",
                    ],
                },
            }
        )

    def update_user_prompt(self, user_input: str):
        """Update the user prompt with the current action and player attributes."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                player_action=user_input,
                player_description=self.player.description,
                history=self.history.history_prompt(),
            )
        )

    def send(self, user_input: str) -> AbilityCheckResponse:
        self.update_user_prompt(user_input)

        """Send the request to the LLM and return the response."""
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=50,
            temperature=0.4,
        )
        return AbilityCheckResponse.process_response(ai_response)
