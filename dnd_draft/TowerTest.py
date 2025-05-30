import AIResponse, LLMModel, Tower, AIClassifyActionResponse

from importlib import reload
from AIClassifyActionResponse import ClassifyActionResponse

# Initialize the model once
print("Loading LLM (this will take a moment)...")
llm = LLMModel.LLMModel()

my_dm = Tower.DungeonMaster(llm)

# fake_ai_response = AIResponse.AIResponseSuccess(
#     success=True,
#     message="",
#     respond_message="As you step into the tower, you find yourself on the first floor. The air is stale and musty, and the walls are adorned with cobweb-covered tapestries. The room is dimly lit by flickering torches, casting eerie shadows on the stone floor. Ahead of you, a grand staircase curves upward, disappearing into the darkness.",
#     suggested_actions=[
#         "Explore the cobweb-covered tapestries",
#         "Head up the staircase to explore the upper floors",
#         "Custom action (type your own)",
#     ],
#     health_change=0,
#     next_floor=False,
#     inventory_changes={},
#     status_effects=[],
#     game_over=False,
# )


def reload_towerDM():
    """Reload only the Tower class while keeping the LLM in memory"""
    # Reload the modules
    reload(Tower)
    reload(AIResponse)
    reload(AIClassifyActionResponse)
    return Tower.DungeonMaster(llm)


def test_setup_floor_user_prompt():
    dm = reload_towerDM()
    print(dm.setup_floor_user_prompt())


def test_start_game():
    dm = reload_towerDM()
    dm.start_game()

    # Check floor history for the first floor exists or not
    print(dm.state.floor_history[1])


def test_generate_floor_description():
    dm = reload_towerDM()
    dm.start_game()
    response = dm.generate_floor_description()
    print(response)
    print(dm.state.format_history())
    print(response.ai_response)


def test_setup_classify_action_user_prompt():
    dm = reload_towerDM()
    dm.start_game()

    with open("test/1/ai_response.json") as f:
        fake_ai_response = AIResponse.AIResponse.process_response(f.read())
    dm.handle_ai_response(fake_ai_response)

    print(dm.state.format_history())

    print(
        dm.setup_classify_action_user_prompt(
            "I take out my RPG and start shooting the tower."
        )
    )


def test_classify_action():
    dm = reload_towerDM()
    dm.start_game()
    dm.handle_ai_response(fake_ai_response)

    suggested_action = fake_ai_response.get_suggested_action()
    result = dm.classify_action(suggested_action)

    print(result)
    print(result.ai_response)


def test_invalid_action():
    dm = reload_towerDM()
    dm.start_game()
    dm.handle_ai_response(fake_ai_response)

    result = dm.classify_action("I take out my RPG and start shooting the tower.")

    print(result)
    print(result.ai_response)


def test_handle_classify_action_response():
    dm = reload_towerDM()
    dm.start_game()
    dm.handle_ai_response(fake_ai_response)

    print(dm.state.player)
    dm.handle_classify_action_response(fake_ai_classify_action_response)
    print(dm.state.player)

    # print(dm.state.format_history())
    print(dm.state.floor_history[1])

def run_story_line():
    dm = reload_towerDM()
    dm.start_game()
    with open("test/1/ai_response.json") as f:
        fake_ai_response = AIResponse.AIResponse.process_response(f.read())
    
    print(fake_ai_response.respond_message)
    print(fake_ai_response.suggested_actions)
    
    suggested_action = fake_ai_response.get_suggested_action()
    print(suggested_action)

    with open("test/1/classify_action.json") as f:
        fake_ai_classify_action_response = ClassifyActionResponse.process_response(f.read())

    print(fake_ai_classify_action_response.ai_response)
    

