import enum
from dataclasses import dataclass
import json


@enum.unique
class Rarity(str, enum.Enum):
    STARTER = "Starter"
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"


@dataclass
class Weapon:
    name: str
    rarity: Rarity
    type: str
    description: str
    base_damage: int


@dataclass
class Item:
    name: str
    rarity: Rarity
    description: str
    effect: str

    def to_prompt(self):
        to_print = ""
        to_print += f"Name: {self.name}\n"
        to_print += f"Rarity: {self.rarity.value}\n"
        to_print += f"Description: {self.description}\n"
        to_print += f"Effect: {self.effect}\n"
        return to_print

    def to_dict(self) -> dict:
        """Convert the class to a dictionary."""
        return {
            "name": self.name,
            "rarity": self.rarity.value,
            "description": self.description,
            "effect": self.effect,
        }

    def __json__(self) -> dict:
        """Make the class JSON-serializable."""
        return self.to_dict()
