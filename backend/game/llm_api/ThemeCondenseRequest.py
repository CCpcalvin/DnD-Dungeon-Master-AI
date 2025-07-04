from __future__ import annotations
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from game.models.LLMProvider import LLMProvider

from pydantic import Field


class ThemeCondenseResponseModel(LLMResponseModel):
    theme: str = Field(
        ...,
        description="A 20 words or less description of the overall theme",
    )
    player_backstory: str = Field(
        ...,
        description="A 30 words or less description of the player's backstory",
    )


class ThemeCondenseRequest(LLMRequest):
    @property
    def prompt_file(self) -> str:
        return "theme_condense.txt"

    @property
    def ResponseModel(self) -> type[ThemeCondenseResponseModel]:
        return ThemeCondenseResponseModel

    def __init__(self, provider: LLMProvider):
        super().__init__(provider)

    def update_user_prompt(self, theme: str, player_backstory: str):
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme, player_backstory=player_backstory
            )
        )

    def send(self, theme: str, player_backstory: str):
        """
        Send the theme condense request to the LLM.

        Args:
            theme: The original theme text
            player_backstory: The player's backstory

        Returns:
            ThemeCondenseResponse: The condensed theme and backstory
        """
        self.update_user_prompt(theme, player_backstory)

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=200,
            temperature=0.5,
        )
