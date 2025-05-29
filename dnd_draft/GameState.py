from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import random, json


@dataclass
class Player:
    name: str
    health: int
    inventory: Dict[str, int]

    # Attributes
    strength: int
    dexterity: int
    intelligence: int
    wisdom: int
    charisma: int

    min_per_attr: int = 1  # Ensure no stat is zero
    max_per_attr: int = 9

    @classmethod
    def create_with_random_stats(cls, name: str) -> Player:
        """
        Create a new Player with randomized stats that sum to 35,
        with each stat having a maximum of 9.
        """
        # Define the attributes we want to randomize
        attributes = [
            "health",
            "strength",
            "dexterity",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        total_points = 30

        # Start with minimum values
        stats = {attr: cls.min_per_attr for attr in attributes}
        remaining_points = total_points - (cls.min_per_attr * len(attributes))

        # Distribute remaining points randomly
        while remaining_points > 0:
            # Pick a random attribute to increase
            attr = random.choice(attributes)
            # Only increase if below max
            if stats[attr] < cls.max_per_attr:
                stats[attr] += 1
                remaining_points -= 1

        # Create and return the player
        return cls(
            name=name,
            health=stats["health"],
            inventory={"gold": 5},
            strength=stats["strength"],
            dexterity=stats["dexterity"],
            intelligence=stats["intelligence"],
            wisdom=stats["wisdom"],
            charisma=stats["charisma"],
        )

    def update_attributes(self, attribute_changes: dict) -> None:
        """
        Update player attributes based on the provided dictionary.

        Args:
            attribute_changes: Dictionary of attribute names and their changes.
                             Positive values increase, negative values decrease the attribute.
        """
        for attr, change in attribute_changes.items():
            if hasattr(self, attr):
                current_value = getattr(self, attr)

                # Ensure the attribute doesn't go below 1
                new_value = max(self.min_per_attr, current_value + change)
                new_value = current_value + change
                if new_value <= self.max_per_attr and new_value >= self.min_per_attr:
                    setattr(self, attr, new_value)


class FloorHistory:
    content: list[dict] = []
    summary: str = ""

    def add_narrative(self, narrative: str):
        self.content.append({"narrative": narrative})

    def add_player_actions(self, actions: str, success: bool):
        self.content.append({"player": actions, "success": success})

    def has_summary(self):
        return len(self.summary) > 0

    def has_history(self):
        return len(self.content) > 0

    def __str__(self):
        if not self.has_history():
            return f"No history available"

        return f"{self.content}"


class GameState:
    current_floor: int = 1
    player: Player = None
    inventory: Dict[str, int] = None
    floor_history: Dict[int, FloorHistory] = {}

    def __str__(self):
        return f"Floor: {self.current_floor}\nPlayer: {self.player}\nInventory: {self.inventory}\nFloor History Index: {self.floor_history.keys()}"

    def format_history(self) -> str:
        history_list = {}
        for floor, floor_history in self.floor_history.items():
            if floor_history.has_summary():
                history_list[f"Floor {floor}"] = floor_history.summary
            else:
                history_list[f"Floor {floor}"] = floor_history.__str__()

        return json.dumps(history_list)
