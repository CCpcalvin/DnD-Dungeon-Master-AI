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


@enum.unique
class WeaponType(str, enum.Enum):
    SWORD = "Sword"
    AXE = "Axe"
    BOW = "Bow"
    STAFF = "Staff"
    DAGGER = "Dagger"
    SPEAR = "Spear"
    CLUB = "Club"
    MACE = "Mace"


@dataclass
class Weapon:
    name: str
    rarity: Rarity
    type: WeaponType
    description: str
    base_damage: int


@dataclass
class Item:
    name: str
    rarity: Rarity
    description: str
    effect: str