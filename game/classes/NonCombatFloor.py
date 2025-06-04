import os, random
from typing import Union, Optional

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.models.LLMProvider import LLMProvider
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.classes.RollResults import RollResult

from game.llm_api.NonCombatFloorIntroRequest import (
    NonCombatFloorIntroRequest,
    NonCombatFloorIntroResponseModel,
)

from game.llm_api.ClassifyNonCombatActionRequest import (
    ClassifyNonCombatActionRequest,
    ClassifyNonCombatActionResponseModel,
)

from game.llm_api.AbilityCheckRequest import AbilityCheckRequest

from game.llm_api.AbilityCheckResolutionRequest import (
    AbilityCheckResolutionRequest,
    AbilityCheckResolutionResponseModel,
)

from game.llm_api.ItemUseResolutionRequest import (
    ItemUseResolutionRequest,
    ItemUseResolutionResponseModel,
)

from game.llm_api.SuggestActionRequest import SuggestActionRequest
from game.Const import GAME_PATH


class NonCombatFloor:
    mocks_dir = os.path.join(GAME_PATH, "test", "mock")

    def __init__(self, theme: str, player: Player, provider: LLMProvider):
        self.theme = theme
        self.player = player
        self.provider = provider

        # History
        self.history: FloorHistory = FloorHistory()

        # Request objects
        self.intro_request = NonCombatFloorIntroRequest(
            provider, theme, player.description
        )
        self.classify_action_request = ClassifyNonCombatActionRequest(
            provider,
            theme,
            player,
            self.history,
        )
        self.ability_check_request = AbilityCheckRequest(
            provider,
            player,
            self.history,
        )
        self.ability_check_resolution_request = AbilityCheckResolutionRequest(
            provider,
            theme,
            player,
            self.history,
        )
        self.suggest_action_request = SuggestActionRequest(
            provider,
            theme,
            player,
            self.history,
        )
        self.item_use_resolution_request = ItemUseResolutionRequest(
            provider,
            theme,
            player,
            self.history,
        )

    def reload(self):
        return NonCombatFloor(self.theme, self.player, self.provider)

    def init_mock(self, mock: int):
        """
        Save the response to a file, such that we do not need to regenerate it.
        It is for testing purpose.
        """
        self.current_mock_dir = os.path.join(self.mocks_dir, f"{mock}")

        if not os.path.exists(self.current_mock_dir):
            os.makedirs(self.current_mock_dir)

    def init_floor(self, mock: Optional[int] = None):
        if mock is not None:
            self.init_mock(mock)

        # Init the data
        self.end = False

        # Randomize the floor type
        self.floor_type = random.choice(list(NonCombatFloorType))

        print("(System): Generating floor description...")
        #! TODO: Error handling
        # Get the floor description and investigation hook
        intro_response: NonCombatFloorIntroResponseModel = (
            self.intro_request.send_and_save_to_mock(
                mocks_dir=self.mocks_dir,
                save_file_name="non_combat_floor_intro_response.json",
                mock=mock,
                floor_type=self.floor_type,
            )
        )

        # Set the description
        self.description = intro_response.description

        narrative = self.description + " " + intro_response.investigation_hook
        print(narrative)

        self.history.add_narrative(intro_response.summary)

        print("What do you want to do?")
        for i, action in enumerate(intro_response.suggested_actions):
            print(f"{i + 1}. {action}")
        print(f"{i + 2}. Go to the next floor.")
        print(f"{i + 3}. Write your own action.")

    def handle_user_input(self, user_input: str):
        print("(System): Classifying your action...")

        #! TODO: Error handling
        classify_action_response = self.classify_action_request.send(user_input)

        if classify_action_response.narrative_consistency is False:
            print(
                "(System): Your action is not consistent with the narrative. Please re-input your action"
            )
            return

        if classify_action_response.action_type == "unknown":
            print(
                "(System): System cannot classify your action. Please re-input your action"
            )
            return

        if classify_action_response.action_type == "ability_check":
            self.handle_ability_check(user_input)

        elif classify_action_response.action_type == "use_item":
            self.handle_use_item()

        elif classify_action_response.action_type == "go_to_next_floor":
            self.go_to_next_floor()

    def handle_ability_check(self, user_input: str):
        #! TODO: Error handling
        ability_check_response = self.ability_check_request.send(user_input)

        # Calculate the player's score
        roll = random.randint(1, 10)
        score = roll + self.player.get_attribute(ability_check_response.attribute)

        # Calculate the roll result
        if roll == 10:
            # Critical Success
            roll_result = RollResult.CRITICAL_SUCCESS

        elif roll == 1:
            # Critical Failure
            roll_result = RollResult.CRITICAL_FAILURE

        else:
            if score >= ability_check_response.difficulty_class:
                roll_result = RollResult.SUCCESS

            else:
                roll_result = RollResult.FAILURE

        # Print it out for player
        print(
            f"(System): Score: {score} = {roll} (Roll) + {self.player.get_attribute(ability_check_response.attribute)} ({ability_check_response.attribute}). The DC is {ability_check_response.difficulty_class}. It is {roll_result.value}."
        )

        # Get the story extension
        #! TODO: Error handling
        story_extend_response = self.ability_check_resolution_request.send(
            player_action=user_input,
            roll_result=roll_result,
        )

        # Update the player's health
        #! TODO: Check player health! If it goes below 0, it will be game over
        self.player.update_health(story_extend_response.health_change)
        if self.player.current_health <= 0:
            print("(System): You are defeated.")
            self.end = True
            return

        # Add to the history
        self.history.add_player_actions(user_input, roll_result)

        return self.handle_resolution(story_extend_response)

    def handle_use_item(self):
        item_index = int(
            input("(System): Please input the item index you want to use.")
        )
        user_input = input("(System): How do you use the item?")

        return self.use_item_resolution(item_index, user_input)

    def use_item_resolution(self, item_index: int, user_input: str):
        print("(System): Resolving item usage...")
        #! TODO: Error handling
        item_use_resolution_response = self.item_use_resolution_request.send(
            item_to_use=self.player.inventory[item_index],
            user_input=user_input,
        )

        if item_use_resolution_response.is_item_consumed:
            self.player.inventory.pop(item_index)

        return self.handle_resolution(item_use_resolution_response)

    def handle_resolution(
        self,
        response: Union[
            ItemUseResolutionResponseModel, AbilityCheckResolutionResponseModel
        ],
    ):
        # Print the story
        print(response.narrative)

        # Add the user input and story extension to the history
        self.history.add_narrative(response.summary)

        # Check if the event is ended
        #! TODO:
        if response.is_event_ended:
            print("(System): The event is ended.")
            self.end = True
            return

        else:
            # Suggest some actions for the player to take
            print("(System): Suggesting actions...")
            #! TODO: Error handling
            suggest_action_response = self.suggest_action_request.send(
                recent_history=response.narrative,
            )

            # Print the suggested actions
            print("(System): Suggested actions:")
            for i, action in enumerate(suggest_action_response.suggested_actions):
                print(f"{i + 1}. {action}")

            print(f"{i + 2}. Write your own action.")
            return

    def go_to_next_floor(self):
        #! TODO: Think about what information need to be sent back to DM
        self.end = True
