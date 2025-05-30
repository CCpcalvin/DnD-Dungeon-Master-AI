from __future__ import annotations
from dataclasses import dataclass, field
import json


@dataclass
class ActionConsequence:
    message: str
    suggested_actions: List[str]
    health_change: int
    inventory_changes: dict
    attribute_changes: dict

    @classmethod
    def from_dict(cls, data: dict) -> "ActionConsequence":
        """Create an ActionConsequence from a dictionary."""
        return cls(
            message=data.get("message", ""),
            suggested_actions=data.get("suggested_actions", []),
            health_change=data.get("health_change", 0),
            inventory_changes=data.get("inventory_changes", {}),
            attribute_changes=data.get("attribute_changes", {}),
        )


@dataclass
class ClassifyActionResponse:
    """Response for successful AI responses"""

    success: bool  # This means we can read the AI response successfully or not
    message: str
    player_action: str
    ai_response: str = field(repr=False)

    @classmethod
    def process_response(
        cls, player_action: str, ai_response: str
    ) -> ClassifyActionResponse:
        try:
            data = json.loads(ai_response)
            narrative_consistency = data.get("narrative_consistency", "")

            if narrative_consistency == True:
                return ClassifyActionSuccess(
                    success=True,
                    message="",
                    player_action=player_action,
                    action_type=data.get("action_type", ""),
                    relevant_attribute=data.get("relevant_attribute", ""),
                    difficulty_class=data.get("difficulty_class", 7),
                    success_response=ActionConsequence.from_dict(
                        data.get("success_response", "")
                    ),
                    failure_response=ActionConsequence.from_dict(
                        data.get("failure_response", "")
                    ),
                    ai_response=ai_response,
                )

            else:
                return ClassifyActionNarrativeInconsistency(
                    success=True,
                    message="Narrative Inconsistency",
                    player_action=player_action,
                    ai_response=ai_response,
                )

        except (json.JSONDecodeError, KeyError):
            return ClassifyActionInvalidJsonError(
                success=False,
                message="Invalid JSON",
                ai_response=ai_response,
                player_action=player_action,
            )

        except Exception as e:
            return ClassifyActionUnknownError(
                success=False,
                message=str(e),
                ai_response=ai_response,
                player_action=player_action,
            )


@dataclass
class ClassifyActionSuccess(ClassifyActionResponse):
    """Response for successful AI responses"""

    action_type: str
    relevant_attribute: str
    difficulty_class: int
    success_response: ActionConsequence
    failure_response: ActionConsequence


@dataclass
class ClassifyActionNarrativeInconsistency(ClassifyActionResponse):
    """Error for invalid JSON responses"""

    pass


@dataclass
class ClassifyActionInvalidJsonError(ClassifyActionResponse):
    """Error for invalid JSON responses"""

    pass 


@dataclass
class ClassifyActionUnknownError(ClassifyActionResponse):
    """Unknown Error"""

    pass 
