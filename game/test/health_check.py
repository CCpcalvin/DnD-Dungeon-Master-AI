import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game.models.LLMProvider import ollama
from game.classes.RollResults import RollResult

from game.DungeonMaster import DungeonMaster


if __name__ == "__main__":
    dm = DungeonMaster(provider=ollama())

    dm.init_game()
    floor = dm.non_combat_floor
    player = dm.player

    suggested_actions = floor.init_floor()
    player.update_health(-12)

    suggested_actions = floor.handle_ability_check(
        suggested_actions[0], RollResult.CRITICAL_FAILURE
    )
