from __future__ import annotations

from game.classes.EntityClasses import Player
from game.classes.LLMModel import LLMModel
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.FloorHistory import FloorHistory
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH
from dataclasses import dataclass

import os, json


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
        model: LLMModel,
        theme: str,
        player: Player,
        history: FloorHistory,
    ):
        super().__init__(model)
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
        Classify the user input into one of the following actions:
            - ability_check
            - use_item
            - go_to_next_floor
            - unknown
            - narrative_inconsistency

        Args:
            user_input: The user input

        Returns:
            ClassifyNonCombatActionResponse: The classified action
        """

        # Set the user prompt with the provided values
        self.update_user_prompt(user_input)

        # Get the AI response
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=50,
            temperature=0.4,
        )

        # Process and return the response
        return ClassifyNonCombatActionResponse.process_response(ai_response)
