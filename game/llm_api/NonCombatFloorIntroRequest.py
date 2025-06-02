from __future__ import annotations

from game.classes.LLMModel import LLMModel
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from dataclasses import dataclass

import os, json


@dataclass
class NonCombatFloorIntroResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> NonCombatFloorIntroResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            return NonCombatFloorIntroResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                description=data["description"],
                investigation_hook=data["investigation_hook"],
                suggested_actions=data["suggested_actions"],
                summary=data["summary"],
            )

        except Exception as e:
            return NonCombatFloorIntroResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class NonCombatFloorIntroResponseSuccess(NonCombatFloorIntroResponse):
    description: str
    investigation_hook: str
    suggested_actions: list[str]
    summary: str


@dataclass
class NonCombatFloorIntroResponseError(NonCombatFloorIntroResponse):
    pass


@dataclass
class NonCombatFloorIntroRequest(LLMRequest):
    prompt_file = "non_combat_floor_intro.txt"

    def __init__(self, model: LLMModel, theme: str, player_description: str):
        super().__init__(model)
        self.theme = theme
        self.player_description = player_description

        # Set response format
        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "investigation_hook": {"type": "string"},
                        "suggested_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "summary": {"type": "string"},
                    },
                    "required": [
                        "description",
                        "investigation_hook",
                        "suggested_actions",
                        "summary",
                    ],
                },
            }
        )

    def update_user_prompt(self, floor_type: NonCombatFloorType):
        """Generate the user prompt by filling in the template with provided values."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player_description,
                floor_type=floor_type.value,
            )
        )

    def send(self, floor_type: NonCombatFloorType) -> NonCombatFloorIntroResponse:
        """
        Generate a floor description and investigation hook based on the provided floor type.

        Args:
            floor_type: The type of the floor

        Returns:
            NonCombatFloorIntroResponse: The generated floor description and investigation hook
        """

        # Set the user prompt with the provided values
        self.update_user_prompt(floor_type)

        # Get the AI response
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=200,
            temperature=0.8,
        )

        # Process and return the response
        return NonCombatFloorIntroResponse.process_response(ai_response)
