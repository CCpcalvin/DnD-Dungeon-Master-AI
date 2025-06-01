import sys

sys.path.append("..")

from game.classes.LLMModel import LLMModel
from game.classes.NonCombatFloor import NonCombatFloor
from game.DungeonMaster import DungeonMaster

# Import the IPython module
try:
    from IPython import get_ipython

    ipython = get_ipython()
    if ipython is not None:
        # Get the model from IPython's user namespace
        model = ipython.user_ns.get("model")
        if model is None:
            raise ValueError("No 'model' variable found in IPython namespace")
    else:
        raise ImportError("Not running in IPython")
except (ImportError, ValueError) as e:
    print(f"Warning: {e}. Creating a new model instance.")
    from game.classes.LLMModel import LLMModel

    model = LLMModel()


def test_ability_check():
    global model

    # Setup dungeon master
    dungeon_master = DungeonMaster(model)

    # Start the game
    dungeon_master.init_game(mock=True)

    # Get the floor
    floor1 = NonCombatFloor(dungeon_master.theme, dungeon_master.player, model)
    floor1.init_floor(mock=True)

    # Now we can test the ability check
    respond = floor1.ability_check_request.send_and_save(
        save_path="./test/mock/ability_check_response.json",
        user_input="Examine the symbol more closely",
    )
    print(respond)

    respond = floor1.ability_check_request.send_and_save(
        save_path="./test/mock/ability_check_response_1.json",
        user_input="Search the shelves for a specific tome",
    )
    print(respond)


test_ability_check()
