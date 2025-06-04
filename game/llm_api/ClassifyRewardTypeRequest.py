from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponseModel

from pydantic import Field
from typing import Literal


class ClassifyRewardTypeResponseModel(LLMResponseModel):
    reward_type: Literal["heal", "max_health_increase", "attribute_increase"] = Field(
        ..., description="The type of reward"
    )


class ClassifyRewardTypeRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "classify_reward_type.txt"

    @property
    def ResponseModel(self):
        return ClassifyRewardTypeResponseModel

    def __init__(
        self, provider: LLMProvider, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

    def update_user_prompt(self, recent_history: str):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                recent_history=recent_history,
            )
        )

    def send(self, recent_history: str) -> ClassifyRewardTypeResponseModel:
        """Send the request and return the response."""
        self.update_user_prompt(recent_history)
        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=50,
            temperature=0.4,
        )
