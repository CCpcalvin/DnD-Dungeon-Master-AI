import sys
sys.path.append("..")

from importlib import reload

from game.classes.LLMModel import LLMModel

from game import Const, DungeonMaster
from game.classes import FloorHistory, ItemClasses, EntityClasses
from game.llm_api import LLMRequest, BackgroundRequest, WeaponGenerationRequest, ThemeCondenseRequest

# Initialize the model once
print("Loading LLM (this will take a moment)...")
model = LLMModel()


def reload_game_modules():
    """Reload all game modules for development."""
    print("Reloading game modules...")

    # List of modules to reload in order of dependency
    modules_to_reload = [
        Const,
        FloorHistory,
        ItemClasses,
        EntityClasses,
        LLMRequest,
        BackgroundRequest,
        WeaponGenerationRequest,
        ThemeCondenseRequest,
        DungeonMaster,
    ]

    for module in modules_to_reload:
        print(f"Reloading {module.__name__}...")
        reload(module)

    print("All game modules reloaded successfully!")
    return DungeonMaster.DungeonMaster(model)


dm = reload_game_modules()

