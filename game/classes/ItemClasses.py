import enum
from dataclasses import dataclass


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