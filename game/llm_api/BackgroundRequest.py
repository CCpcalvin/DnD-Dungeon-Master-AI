from __future__ import annotations
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel
from game.models.LLMProvider import LLMProvider

from pydantic import Field


class BackgroundResponseModel(LLMResponseModel):
    theme: str = Field(
        ..., description="A 2-3 sentences description of the overall theme"
    )
    player_backstory: str = Field(
        ..., description="A 1-2 sentences description of the player's backstory"
    )
    player_motivation: str = Field(
        ...,
        description="A 1-2 sentences The player's reason for being here and what they know",
    )


class BackgroundRequest(LLMRequest):
    @property
    def prompt_file(self) -> str:
        return "background.txt"

    @property
    def ResponseModel(self) -> type[BackgroundResponseModel]:
        return BackgroundResponseModel

    def __init__(self, provider: LLMProvider):
        super().__init__(provider)

    def update_user_prompt(self):
        self.set_user_prompt(self.user_prompt_template)

    def send(self):
        self.update_user_prompt()

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=500,
            temperature=0.8,
        )
