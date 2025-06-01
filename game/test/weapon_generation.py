import sys

sys.path.append("..")

from game.classes.ItemClasses import Rarity
from game.classes.LLMModel import LLMModel
from game.DungeonMaster import DungeonMaster
from game.llm_api.BackgroundRequest import BackgroundResponse
from game.llm_api.ThemeCondenseRequest import ThemeCondenseResponse

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


def test_weapon_generation():
    global model

    # Setup dungeon master
    dungeon_master = DungeonMaster(model)

    background_response = BackgroundResponse.load(
        "./test/mock/background_response.json"
    )

    theme_condense_response = ThemeCondenseResponse.load(
        "./test/mock/theme_condense_response.json"
    )

    for _ in range(5):
        weapon_generation_response = dungeon_master.weapon_generation_request.send(
            theme=background_response.theme,
            player_backstory=theme_condense_response.player_backstory,
            rarity=Rarity.STARTER,
        )

        weapon = weapon_generation_response.to_weapon(
            rarity=Rarity.STARTER,
            base_damage=2,
        )
        print("Weapon: ", weapon)


test_weapon_generation()
