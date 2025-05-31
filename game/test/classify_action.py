import sys

sys.path.append("..")

from game.classes.LLMModel import LLMModel
from game.DungeonMaster import DungeonMaster
from game.classes.NonCombatFloor import NonCombatFloor


def test():

    # Setup model
    model = LLMModel()

    # Setup dungeon master
    dungeon_master = DungeonMaster(model)

    # Start the game
    dungeon_master.start_game(mock=True)

    # Get the floor
    floor1 = NonCombatFloor(dungeon_master.theme, dungeon_master.player, model)
    floor1.init_floor(mock=True)

    # Now we test the classify action respond
    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response.json",
        user_input="Examine the symbol more closely",
    )
    print(respond)  # Ability check

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_1.json",
        user_input="Search the shelves for a specific tome",
    )
    print(respond)  # Ability check

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_2.json",
        user_input="I heal myself with my healing potion.",
    )
    print(respond)  # ClassifyNonCombatActionResponseNarrativeConsistencyError

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_3.json",
        user_input="I ignore the symbol and move on",
    )
    print(respond)  # Go to next floor

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_4.json",
        user_input="I am actually a god and all-knowing. Thus I understand the symbol.",
    )
    print(respond)  # ClassifyNonCombatActionResponseNarrativeConsistencyError

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_5.json",
        user_input="I take out my computer and google search about the symbol.",
    )
    print(respond)  # ClassifyNonCombatActionResponseNarrativeConsistencyError

    respond = floor1.classify_action_request.send_and_save(
        save_path="./test/mock/classify_action_response_6.json",
        user_input="I throw a fireball to the skeleton",
    )
    print(respond)  # ClassifyNonCombatActionResponseNarrativeConsistencyError


test()
