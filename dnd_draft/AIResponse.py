from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AIResponse:
    """Base class for AI responses"""

    success: bool
    message: str

    @classmethod
    def create_error(cls, message: str) -> AIResponse:
        """Helper to create an error response"""
        return AIResponse(success=False, message=message)

    @classmethod
    def process_response(cls, ai_response: str) -> AIResponse:
        try:
            data = json.loads(ai_response)

            # If successful
            return AIResponseSuccess(
                success=True,
                message="",
                respond_message=data.get("respond_message", ""),
                suggested_actions=data.get("suggested_actions", []),
                health_change=data.get("health_change", 0),
                next_floor=data.get("next_floor", False),
                inventory_changes=data.get("inventory_changes", {}),
                status_effects=data.get("status_effects", []),
                game_over=data.get("game_over", False),
            )

        except (json.JSONDecodeError, KeyError):
            return AIResponseInvalidJsonError(ai_respond=ai_response)

        except:
            return AIResponseUnknownError(ai_respond=ai_response)
    
    # Get the first suggested action
    def get_suggested_action(self):
        return self.suggested_actions[0]


@dataclass
class AIResponseSuccess(AIResponse):
    """Response for successful AI responses"""

    respond_message: str
    suggested_actions: List[str]
    health_change: int
    next_floor: bool
    inventory_changes: Optional[dict]
    status_effects: Optional[List[str]]
    game_over: bool


@dataclass
class AIResponseInvalidJsonError(AIResponse):
    """Error for invalid JSON responses"""

    success: bool = False
    message: str = "Invalid JSON"
    ai_respond: str = ""


@dataclass
class GameAIUnknownError(AIResponse):
    """Unknown Error"""

    success: bool = False
    message: str = "Unknown Error"
    ai_respond: str = ""
