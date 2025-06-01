from __future__ import annotations

from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.LLMModel import LLMModel
from game.classes.ItemClasses import Rarity, Weapon
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import os, json
from dataclasses import dataclass


@dataclass
class WeaponGenerationResponse(LLMResponse):

    @classmethod
    def process_response(cls, ai_response: dict) -> WeaponGenerationResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            return WeaponGenerationResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                name=data["name"],
                type=data["type"],
                description=data["description"],
                special_ability=data["special_ability"],
            )

        except Exception as e:
            return WeaponGenerationResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class WeaponGenerationResponseSuccess(WeaponGenerationResponse):
    name: str
    type: str
    description: str
    special_ability: str

    def to_weapon(self, rarity: Rarity, base_damage: int):
        return Weapon(
            name=self.name,
            rarity=rarity,
            type=self.type,
            description=self.description,
            base_damage=base_damage,
        )


@dataclass
class WeaponGenerationResponseError(WeaponGenerationResponse):
    pass


class WeaponGenerationRequest(LLMRequest):
    def __init__(self, model: LLMModel):
        super().__init__(model)

        # Load system prompt
        with open(os.path.join(SYSTEM_PROMPT_PATH, "weapon.txt"), "r") as f:
            self.system_prompt = f.read()
            self.set_system_prompt(self.system_prompt)

        # Load user prompt template
        with open(os.path.join(USER_PROMPT_PATH, "weapon.txt"), "r") as f:
            self.user_prompt_template = f.read()

        # Set response format
        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "special_ability": {"type": "string"},
                    },
                    "required": [
                        "name",
                        "type",
                        "description",
                        "special_ability",
                    ],
                },
            }
        )

    def update_user_prompt(self, theme: str, player_backstory: str, rarity: Rarity):
        """Generate the user prompt by filling in the template with provided values."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme,
                player_backstory=player_backstory,
                rarity=rarity.value,
            )
        )

    def send(
        self, theme: str, player_backstory: str, rarity: Rarity
    ) -> WeaponGenerationResponse:
        """
        Generate a weapon based on the provided theme and player backstory.

        Args:
            theme: The theme of the story/game
            player_backstory: The player's backstory to tailor the weapon to
            rarity: The rarity of the weapon

        Returns:
            WeaponResponse: The generated weapon details or an error response
        """

        # Set the user prompt with the provided values
        self.update_user_prompt(theme, player_backstory, rarity)

        # Get the AI response
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=200,
            temperature=0.8,
        )

        # Process and return the response
        return WeaponGenerationResponse.process_response(ai_response)
