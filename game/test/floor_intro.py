import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game.models.LLMProvider import ollama
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.DungeonMaster import DungeonMaster


def test_intro():
    dm = DungeonMaster(provider=ollama())

    dm.init_game()
    floor = dm.non_combat_floor

    # for i in range(5):
    #     print("")
    #     print(i)
    #     floor.init_floor(NonCombatFloorType.TREASURE)

    # for i in range(5):
    #     print("")
    #     print(i)
    #     floor.init_floor(NonCombatFloorType.TREASURE_WITH_TRAP)

    for i in range(5):
        print("")
        print(i)
        floor.init_floor(NonCombatFloorType.HIDDEN_TRAP)

    for i in range(5):
        print("")
        print(i)
        floor.init_floor(NonCombatFloorType.NPC_ENCOUNTER)


if __name__ == "__main__":
    test_intro()



