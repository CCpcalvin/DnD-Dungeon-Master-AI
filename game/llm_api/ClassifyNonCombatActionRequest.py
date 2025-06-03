from __future__ import annotations

from game.classes.EntityClasses import Player
from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.FloorHistory import FloorHistory
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Literal

import json


class ClassifyNonCombatActionResponseModel(BaseModel):
    action_type: Literal["ability_check", "use_item", "go_to_next_floor", "unknown"] = (
        Field(
            ...,
            description="The type of action: 'ability_check', 'use_item', 'go_to_next_floor', or 'unknown'",
        )
    )
    narrative_consistency: bool = Field(
        ..., description="Whether the user input is consistent with the narrative"
    )


@dataclass
class ClassifyNonCombatActionResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> ClassifyNonCombatActionResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            if not data["narrative_consistency"]:
                return ClassifyNonCombatActionResponseNarrativeConsistencyError(
                    success=True,
                    message="",
                    ai_response=ai_response,
                    action_type=data["action_type"],
                )
            elif data["action_type"] == "unknown":
                return ClassifyNonCombatActionResponseUnknownError(
                    success=True,
                    message="",
                    ai_response=ai_response,
                    action_type=data["action_type"],
                )

            return ClassifyNonCombatActionResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                action_type=data["action_type"],
            )

        except Exception as e:
            return ClassifyNonCombatActionResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class ClassifyNonCombatActionResponseSuccess(ClassifyNonCombatActionResponse):
    action_type: str


@dataclass
class ClassifyNonCombatActionResponseNarrativeConsistencyError(
    ClassifyNonCombatActionResponseSuccess
):
    pass


@dataclass
class ClassifyNonCombatActionResponseUnknownError(
    ClassifyNonCombatActionResponseSuccess
):
    pass


@dataclass
class ClassifyNonCombatActionResponseError(ClassifyNonCombatActionResponse):
    pass


@dataclass
class ClassifyNonCombatActionRequest(LLMRequest):
    prompt_file = "classify_non_combat_action.txt"

    def __init__(
        self,
        provider: LLMProvider,
        theme: str,
        player: Player,
        history: FloorHistory,
    ):
        super().__init__(provider)
        self.theme = theme
        self.player = player
        self.history = history

        # Set response format
        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "action_type": {"type": "string"},
                        "narrative_consistency": {"type": "boolean"},
                    },
                    "required": ["action_type", "narrative_consistency"],
                },
            }
        )

    def update_user_prompt(self, user_input: str):
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=self.theme,
                player_description=self.player.description,
                player_inventory=self.player.inventory_prompt(),
                history=self.history.history_prompt(),
                user_input=user_input,
            )
        )

    def send(self, user_input: str) -> ClassifyNonCombatActionResponse:
        """
        Send the classification request to the LLM.

        Args:
            user_input: The player's input text to classify

        Returns:
            ClassifyNonCombatActionResponse: The classified action type and narrative consistency
        """
        self.update_user_prompt(user_input)

        ai_response = self.provider.get_completion(
            response_model=ClassifyNonCombatActionResponseModel,
            messages=self.messages,
            max_tokens=50,
            temperature=0.1,
        )
        return ClassifyNonCombatActionResponse.process_response(ai_response)
