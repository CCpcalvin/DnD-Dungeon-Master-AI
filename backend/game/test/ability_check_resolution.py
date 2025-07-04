import sys
import time

sys.path.append("..")

from IPython import get_ipython

from game.classes.LLMModel import LLMModel
from game.classes.NonCombatFloor import NonCombatFloor
from game.classes.RollResults import RollResult
from game.DungeonMaster import DungeonMaster

try:
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


def test_ability_check_resolution():
    global model

    # Setup dungeon master
    dungeon_master = DungeonMaster(model)

    # Start the game
    dungeon_master.init_game(mock=True)

    # Get the floor
    floor1 = NonCombatFloor(dungeon_master.theme, dungeon_master.player, model)
    floor1.init_floor(mock=True)

    t0 = time.time()
    floor1.ability_check_resolution_request.send_and_save(
        save_path="./test/mock/ability_check_resolution_response_success.json",
        player_action="Examine the symbol more closely",
        roll_result=RollResult.SUCCESS,
    )
    print(f"Time taken: {time.time() - t0}")

    t0 = time.time()
    floor1.ability_check_resolution_request.send_and_save(
        save_path="./test/mock/ability_check_resolution_response_failure.json",
        player_action="Examine the symbol more closely",
        roll_result=RollResult.FAILURE,
    )
    print(f"Time taken: {time.time() - t0}")

    t0 = time.time()
    floor1.ability_check_resolution_request.send_and_save(
        save_path="./test/mock/ability_check_resolution_response_critical_success.json",
        player_action="Examine the symbol more closely",
        roll_result=RollResult.CRITICAL_SUCCESS,
    )
    print(f"Time taken: {time.time() - t0}")

    t0 = time.time()
    floor1.ability_check_resolution_request.send_and_save(
        save_path="./test/mock/ability_check_resolution_response_critical_failure.json",
        player_action="Examine the symbol more closely",
        roll_result=RollResult.CRITICAL_FAILURE,
    )
    print(f"Time taken: {time.time() - t0}")


test_ability_check_resolution()
