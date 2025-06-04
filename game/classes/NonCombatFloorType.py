import enum


class NonCombatFloorType(str, enum.Enum):
    TREASURE = "Treasure"
    TREASURE_WITH_TRAP = "Treasure with Trap"
    HIDDEN_TRAP = "Hidden Trap"
    NPC_ENCOUNTER = "NPC Encounter"
