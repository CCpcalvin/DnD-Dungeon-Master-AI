import sys

sys.path.append("..")

from game.classes.ItemClasses import Item, Rarity
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
    from game.models.LLMProvider import Local_LLAMAProvider

    model = Local_LLAMAProvider()


def test_item_identification():
    global model

    # Setup dungeon master
    dungeon_master = DungeonMaster(model)

    # Start the game
    dungeon_master.init_game(mock=True)

    # Get the floor
    floor1 = NonCombatFloor(dungeon_master.theme, dungeon_master.player, model)
    floor1.init_floor(mock=True)

    # Add some items to the player
    player = floor1.player
    player.inventory.append(
        Item(
            name="Healing Potion",
            rarity=Rarity.COMMON,
            description="A red bottle with a skull and crossbones on it.",
            effect="This item heals 2 HP when used.",
        )
    )

    player.inventory.append(
        Item(
            name="Healing Scroll",
            rarity=Rarity.COMMON,
            description="A scroll about 'healing'.",
            effect="This item heals 5 HP when used.",
        )
    )

    player.inventory.append(
        Item(
            name="Long sword",
            rarity=Rarity.COMMON,
            description="Just a normal long sword.",
            effect="This item deals 2 damage when used.",
        )
    )

    player.inventory.append(
        Item(
            name="Sword of Light and Flame",
            rarity=Rarity.LEGENDARY,
            description="Storied sword and treasure of Caria Manor.\nOne of the legendary armaments.\n\nAstrologers, who preceded the sorcerers, established themselves in mountaintops that nearly touched the sky, and considered the Fire Giants their neighbors.",
            effect="This item deals 5 damage when used.",
        )
    )

    # Handle the item identification
    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_1.json",
        user_input="I drink my healing potion to heal myself.",
    )
    print(response)

    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_2.json",
        user_input="I decide to do some healing.",
    )
    print(response)

    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_2.json",
        user_input="I use my sword to break the vase.",
    )
    print(response)

    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_3.json",
        user_input="I use my sword of light and flame to break the vase.",
    )
    print(response)

    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_4.json",
        user_input="I use my short sword to break the vase.",
    )
    print(response)

    response = floor1.item_identification_request.send_and_save(
        save_path="./test/mock/item_identification_response_5.json",
        user_input="I take out the key to unlock the door.",
    )
    print(response)


test_item_identification()
