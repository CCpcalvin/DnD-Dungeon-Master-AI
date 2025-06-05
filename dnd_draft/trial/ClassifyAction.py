import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from LLMModel import LLMModel


class ActionType(Enum):
    ABILITY_CHECK = "ability_check"
    USE_ITEM = "use_item"
    GO_TO_NEXT_FLOOR = "go_to_next_floor"


class AttributeType(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


@dataclass
class ClassifiedAction:
    narrative_consistency: bool
    action_type: ActionType
    relevant_attribute: Optional[AttributeType] = None
    difficulty_class: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "narrative_consistency": self.narrative_consistency,
            "action_type": self.action_type.value,
            "relevant_attribute": (
                self.relevant_attribute.value if self.relevant_attribute else None
            ),
            "difficulty_class": self.difficulty_class,
        }


class ClassifyAction:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        with open("./trial/prompt/system_classify_action_prompt.txt", "r") as f:
            return f.read()

    # def _load_system_prompt(self) -> str:
    #     with open("./trial/prompt/short.txt", "r") as f:
    #         return f.read()

    # def _load_user_prompt(self, player_action: str) -> str:
    #     with open("./trial/prompt/user_classify_action_prompt.txt", "r") as f:
    #         return f.read().format(player_action=player_action)

    # def _load_user_prompt(self) -> str:
    #     with open("./trial/prompt/action1.txt", "r") as f:
    #         return f.read()

    def _load_user_prompt(self) -> str:
        with open("./trial/prompt/action2.txt", "r") as f:
            return f.read()

    def classify(self) -> ClassifiedAction:
        # Call LLM with the prompt
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": self._load_user_prompt()},
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "narrative_consistency": {"type": "boolean"},
                        "action_type": {"type": "string"},
                        "relevant_attribute": {"type": "string"},
                        "difficulty_class": {"type": "number"},
                    },
                    "required": [
                        "narrative_consistency",
                        "action_type",
                        "relevant_attribute",
                        "difficulty_class",
                    ],
                },
            },
            temperature=0.3,
            max_tokens=50,
        )

        print(response)
