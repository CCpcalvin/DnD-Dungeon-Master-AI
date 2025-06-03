from __future__ import annotations

from game.models.LLMProvider import LLMProvider
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.NonCombatFloorType import NonCombatFloorType

from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List
import json


class NonCombatFloorIntroResponseModel(BaseModel):
    description: str = Field(
        ...,
        description="A detailed description of the floor's environment and atmosphere",
    )
    investigation_hook: str = Field(
        ...,
        description="A narrative hook to engage the player in investigating the floor",
    )
    suggested_actions: List[str] = Field(
        ...,
        min_items=1,
        max_items=2,
        description="List of suggested actions the player might take (1-2 items)",
    )
    summary: str = Field(..., description="A brief summary of the floor's key features")


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

    def __init__(self, provider: LLMProvider, theme: str, player_description: str):
        super().__init__(provider)
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
        Send the non-combat floor intro request to the LLM.

        Args:
            floor_type: The type of non-combat floor

        Returns:
            NonCombatFloorIntroResponse: The generated floor introduction
        """
        self.update_user_prompt(floor_type)

        ai_response = self.provider.get_completion(
            response_model=NonCombatFloorIntroResponseModel,
            messages=self.messages,
            max_tokens=400,
            temperature=0.8,
        )
        return NonCombatFloorIntroResponse.process_response(ai_response)
