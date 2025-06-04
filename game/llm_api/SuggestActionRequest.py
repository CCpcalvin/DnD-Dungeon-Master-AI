from __future__ import annotations
from game.models.LLMProvider import LLMProvider
from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

from game.llm_api.LLMRequest import LLMRequest

from pydantic import BaseModel, Field
from typing import List


class SuggestActionResponseModel(BaseModel):
    suggested_actions: List[str] = Field(
        ...,
        min_items=1,
        max_items=2,
        description="List of suggested actions for the player (1-2 items)",
    )


class SuggestActionRequest(LLMRequest):
    @property
    def prompt_file(self):
        return "suggest_action.txt"

    @property
    def ResponseModel(self):
        return SuggestActionResponseModel

    def __init__(
        self, provider: LLMProvider, theme: str, player: Player, history: FloorHistory
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

    def update_user_prompt(
        self,
        recent_history: str,
    ):
        """Update the user prompt with the current context."""
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                history=self.history.history_prompt(),
                recent_history=recent_history,
            )
        )

    def send(self, recent_history):
        """
        Send the suggest action request to the LLM.

        Returns:
            SuggestActionResponse: The suggested actions for the player
        """
        self.update_user_prompt(recent_history)

        return self.provider.get_completion(
            ResponseModel=self.ResponseModel,
            messages=self.messages,
            max_tokens=200,
            temperature=0.7,
        )
