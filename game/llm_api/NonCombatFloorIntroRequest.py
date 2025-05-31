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


@dataclass
class NonCombatFloorIntroResponseError(NonCombatFloorIntroResponse):
    pass


@dataclass
class NonCombatFloorIntroRequest(LLMRequest):
    def __init__(self, model: LLMModel):
        super().__init__(model)

        # Load system prompt
        with open(
            os.path.join(SYSTEM_PROMPT_PATH, "non_combat_floor_intro.txt"), "r"
        ) as f:
            self.system_prompt = f.read()
            self.set_system_prompt(self.system_prompt)

        # Load user prompt template
        with open(
            os.path.join(USER_PROMPT_PATH, "non_combat_floor_intro.txt"), "r"
        ) as f:
            self.user_prompt_template = f.read()

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
                    },
                    "required": [
                        "description",
                        "investigation_hook",
                        "suggested_actions",
                    ],
                },
            }
        )

    def update_user_prompt(
        self, theme: str, player_description: str, floor_type: NonCombatFloorType
    ):
        """Generate the user prompt by filling in the template with provided values."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme,
                player_description=player_description,
                floor_type=floor_type.value,
            )
        )

    def send(
        self, theme: str, player_description: str, floor_type: NonCombatFloorType
    ) -> NonCombatFloorIntroResponse:
        """
        Generate a floor description and investigation hook based on the provided floor type.

        Args:
            theme: The theme of the story/game
            player_description: The description of the player
            floor_type: The type of the floor

        Returns:
            NonCombatFloorIntroResponse: The generated floor description and investigation hook
        """

        # Set the user prompt with the provided values
        self.update_user_prompt(theme, player_description, floor_type)

        # Get the AI response
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=200,
            temperature=0.8,
        )

        # Process and return the response
        return NonCombatFloorIntroResponse.process_response(ai_response)
