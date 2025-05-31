from __future__ import annotations
from game.llm_api.LLMRequest import LLMRequest, LLMResponse
from game.classes.LLMModel import LLMModel
from game.Const import SYSTEM_PROMPT_PATH, USER_PROMPT_PATH

import os, json
from dataclasses import dataclass


@dataclass
class ThemeCondenseResponse(LLMResponse):
    @classmethod
    def process_response(cls, ai_response: dict) -> ThemeCondenseResponse:
        try:
            data = json.loads(ai_response["choices"][0]["message"]["content"])

            return ThemeCondenseResponseSuccess(
                success=True,
                message="",
                ai_response=ai_response,
                theme=data.get("theme", ""),
                player_backstory=data.get("player_backstory", ""),
            )

        except Exception as e:
            return ThemeCondenseResponseError(
                success=False,
                message=str(e),
                ai_response=ai_response,
            )


@dataclass
class ThemeCondenseResponseSuccess(ThemeCondenseResponse):
    theme: str
    player_backstory: str


@dataclass
class ThemeCondenseResponseError(ThemeCondenseResponse):
    pass


class ThemeCondenseRequest(LLMRequest):
    def __init__(self, model: LLMModel):
        super().__init__(model)

        with open(os.path.join(SYSTEM_PROMPT_PATH, "theme_condense.txt"), "r") as f:
            self.system_prompt = f.read()
            self.set_system_prompt(self.system_prompt)

        with open(os.path.join(USER_PROMPT_PATH, "theme_condense.txt"), "r") as f:
            self.user_prompt_template = f.read()

        self.set_response_format(
            {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "player_backstory": {"type": "string"},
                    },
                    "required": ["theme", "player_backstory"],
                },
            }
        )

    def update_user_prompt(self, theme: str, player_backstory: str):
        self.set_user_prompt(
            self.user_prompt_template.format(
                theme=theme, player_backstory=player_backstory
            )
        )

    def send(self, theme: str, player_backstory: str) -> ThemeCondenseResponse:
        self.update_user_prompt(theme, player_backstory)
        ai_response = self.model.get_model().create_chat_completion(
            messages=self.messages,
            response_format=self.response_format,
            max_tokens=100,
            temperature=0.4,
        )
        return ThemeCondenseResponse.process_response(ai_response)
