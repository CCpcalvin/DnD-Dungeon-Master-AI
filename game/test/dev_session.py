import sys

sys.path.append("..")

from importlib import reload

from game.classes.LLMModel import LLMModel

from game import Const, DungeonMaster
from game.classes import RollResults
from game.classes import FloorHistory, ItemClasses, EntityClasses
from game.classes import NonCombatFloorType, NonCombatFloor
from game.llm_api import (
    LLMRequest,
    BackgroundRequest,
    WeaponGenerationRequest,
    ThemeCondenseRequest,
    NonCombatFloorIntroRequest,
    ClassifyNonCombatActionRequest,
    AbilityCheckRequest,
    NonCombatStoryExtendRequest,
    SuggestActionRequest,
)

# Initialize the model once
# model = LLMModel()


def reload_game_modules():
    """Reload all game modules for development."""
    print("Reloading game modules...")

    # List of modules to reload in order of dependency
    modules_to_reload = [
        Const,
        RollResults,
        FloorHistory,
        ItemClasses,
        EntityClasses,
        LLMRequest,
        BackgroundRequest,
        WeaponGenerationRequest,
        ThemeCondenseRequest,
        NonCombatFloorType,
        NonCombatFloorIntroRequest,
        ClassifyNonCombatActionRequest,
        AbilityCheckRequest,
        NonCombatStoryExtendRequest,
        SuggestActionRequest,
        NonCombatFloor,
        DungeonMaster,
    ]

    for module in modules_to_reload:
        print(f"Reloading {module.__name__}...")
        reload(module)

    print("All game modules reloaded successfully!")


reload_game_modules()
