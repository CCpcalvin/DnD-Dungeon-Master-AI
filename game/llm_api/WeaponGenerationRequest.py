from __future__ import annotations

from game.llm_api.LLMRequest import LLMRequest
from game.models.LLMProvider import LLMProvider
from game.classes.ItemClasses import Rarity, Weapon
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

from pydantic import BaseModel, Field


class WeaponGenerationResponseModel(BaseModel):
    name: str = Field(..., description="The name of the generated weapon")
    type: str = Field(
        ..., description="The type of weapon (e.g., 'sword', 'staff', 'bow')"
    )
    description: str = Field(
        ...,
        description="A detailed description of the weapon's appearance and properties",
    )
    special_ability: str = Field(
        ...,
        description="A special ability or property that makes this weapon unique",
    )


class WeaponGenerationRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "weapon.txt"

    @property
    def ResponseModel(self):
        return WeaponGenerationResponseModel

    def __init__(self, provider: LLMProvider):
        super().__init__(provider)

    def update_user_prompt(self, theme: str, player_backstory: str, rarity: Rarity):
        """Generate the user prompt by filling in the template with provided values."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme,
                player_backstory=player_backstory,
                rarity=rarity.value,
            )
        )

    def send(self, theme: str, player_backstory: str, rarity: Rarity):
        self.update_user_prompt(theme, player_backstory, rarity)
        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=200,
            temperature=0.8,
        )
