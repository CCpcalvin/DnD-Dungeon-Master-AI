import os, random
from typing import Union, Optional

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

from game.models.LLMProvider import LLMProvider

from game.classes.NonCombatFloorType import NonCombatFloorType
from game.classes.RollResults import RollResult
from game.classes.Progression import Progression

from game.llm_api.NonCombatFloorIntroRequest import (
    NonCombatFloorIntroRequest,
    TreasureRoomIntroRequest,
    TreasureRoomWithTrapIntroRequest,
    HiddenTrapRoomIntroRequest,
    NPCEncounterRoomIntroRequest,
)

from game.llm_api.ClassifyNonCombatActionRequest import (
    ClassifyNonCombatActionRequest,
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
from game.llm_api.ClassifyRewardTypeRequest import ClassifyRewardTypeRequest
from game.llm_api.AttributeRewardRequest import AttributeRewardRequest

from game.Const import GAME_PATH


class NonCombatFloor:
    mocks_dir = os.path.join(GAME_PATH, "test", "mock")

    def __init__(self, theme: str, player: Player, provider: LLMProvider):
        # Floor properties
        self.theme = theme
        self.player = player
        self.provider = provider

        # History
        self.history: FloorHistory = FloorHistory()

        # Request objects
        self.intro_request = NonCombatFloorIntroRequest(
            provider, theme, player.description
        )

        self.treasure_intro_request = (
            TreasureRoomIntroRequest.create_from_non_combat_floor_request(
                self.intro_request
            )
        )

        self.treasure_with_trap_intro_request = (
            TreasureRoomWithTrapIntroRequest.create_from_non_combat_floor_request(
                self.intro_request
            )
        )

        self.hidden_trap_intro_request = (
            HiddenTrapRoomIntroRequest.create_from_non_combat_floor_request(
                self.intro_request
            )
        )

        self.npc_encounter_intro_request = (
            NPCEncounterRoomIntroRequest.create_from_non_combat_floor_request(
                self.intro_request
            )
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

        self.classify_reward_type_request = ClassifyRewardTypeRequest(
            provider,
            theme,
            player,
            self.history,
        )

        self.attribute_reward_request = AttributeRewardRequest(
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

    def init_floor(self, floor_type: Optional[NonCombatFloorType] = None):
        # Init the data
        self.end = False

        # Event completion status
        self.completion: int = 0
        self.penalty: float = 0
        self.fail_penalty: float = 1 / 3
        self.event_length: int = 3
        self.progression = Progression(self.event_length)

        # Randomize the floor type
        if floor_type is None:
            self.floor_type = random.choice(list(NonCombatFloorType))
        else:
            self.floor_type = floor_type

        print("Floor type: ", self.floor_type.value)

        print("(System): Generating floor description...")
        #! TODO: Error handling
        # Get the floor description and investigation hook
        match self.floor_type:
            case NonCombatFloorType.TREASURE:
                intro_response = self.treasure_intro_request.send(
                    floor_type=self.floor_type,
                )

            case NonCombatFloorType.TREASURE_WITH_TRAP:
                intro_response = self.treasure_with_trap_intro_request.send(
                    floor_type=self.floor_type,
                )

            case NonCombatFloorType.HIDDEN_TRAP:
                intro_response = self.hidden_trap_intro_request.send(
                    floor_type=self.floor_type,
                )

            case NonCombatFloorType.NPC_ENCOUNTER:
                intro_response = self.npc_encounter_intro_request.send(
                    floor_type=self.floor_type,
                )

            case _:
                intro_response = self.intro_request.send(
                    floor_type=self.floor_type,
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

        return intro_response.suggested_actions

    def handle_user_input(self, user_input: str, suggested_actions: list[str]):
        print("(System): Classifying your action...")

        # Do a simple string check
        if len(user_input.strip()) < 10:
            print(
                "(System): Your action is too short. Please re-input your action with more details."
            )
            return

        formatted_user_input = user_input.lower().strip()
        for action in suggested_actions:
            # If the user input is a part of the suggested action, handle it as an ability check
            if formatted_user_input in action.lower().strip():
                return self.handle_ability_check(user_input)

        # If the user input is "go to the next floor", skip the floor
        if formatted_user_input in "Go to the next floor.".lower().strip():
            return self.skip_floor(user_input)

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

        #! TODO: Not yet implemented
        elif classify_action_response.action_type == "use_item":
            self.handle_use_item()

        elif classify_action_response.action_type == "go_to_next_floor":
            self.skip_floor(user_input)

    def handle_ability_roll(self, user_input: str):
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

        return roll_result

    def handle_ability_check(
        self, user_input: str, by_pass_roll_result: Optional[RollResult] = None
    ):
        if by_pass_roll_result is None:
            roll_result = self.handle_ability_roll(user_input)
        else:
            roll_result = by_pass_roll_result

        if (
            roll_result == RollResult.CRITICAL_FAILURE
            or roll_result == RollResult.FAILURE
        ):
            # Update panalty
            self.penalty += self.fail_penalty

            # Is the event ended?
            if random.random() < self.penalty:
                self.progression.fail()

        else:
            # Update the progression
            self.progression.progress()

        # Get the story extension
        #! TODO: Error handling
        story_extend_response = self.ability_check_resolution_request.send(
            player_action=user_input,
            roll_result=roll_result,
            progression=self.progression,
            floor_type=self.floor_type,
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
        if self.player.num_of_items() == 0:
            print(
                "(System): I think you are trying to use an item, but you have no items in your inventory. Please re-input your action"
            )
            return

        item_index = int(
            input("(System): Please input the item index you want to use: ")
        )
        user_input = input("(System): How do you use the item?\n")

        return self.use_item_resolution(item_index, user_input)

    def use_item_resolution(self, item_index: int, user_input: str):
        print("(System): Resolving item usage...")
        #! TODO: Error handling
        item_use_resolution_response = self.item_use_resolution_request.send(
            item_to_use=self.player.inventory[item_index],
            user_input=user_input,
            floor_type=self.floor_type,
        )

        if item_use_resolution_response.is_item_consumed:
            self.player.inventory.pop(item_index)

        return self.handle_resolution(item_use_resolution_response)

    def handle_reward(self, reward_type: str, recent_history: str):
        if reward_type == "heal":
            heal_amount = random.randint(1, 4)
            print(f"(System): You are healed for {heal_amount} health.")
            self.player.update_health(heal_amount)

        elif reward_type == "max_health_increase":
            increase_amount = 1
            print(f"(System): Your maximum health is increased by {increase_amount}")
            self.player.max_health += increase_amount

        elif reward_type == "attribute_increase":
            attribute_reward_respond = self.attribute_reward_request.send(
                recent_history=recent_history
            )
            self.player.update_attribute(attribute_reward_respond.attribute, 1)
            print(
                f"(System): Your {attribute_reward_respond.attribute} is increased by 1."
            )

        else:
            print("(System): Unknown reward type. No reward given.")

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
        if self.progression.is_failed():
            print("(System): The event is ended with failure.")
            return self.go_to_next_floor()

        elif self.progression.is_completed():
            print("(System): The event is completed successfully.")

            classify_reward_type_respond = self.classify_reward_type_request.send(
                recent_history=response.narrative,
            )

            # Handle reward
            self.handle_reward(
                classify_reward_type_respond.reward_type,
                recent_history=response.narrative,
            )
            return self.go_to_next_floor()

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
            return suggest_action_response.suggested_actions

    def skip_floor(self, user_input: str):
        if not self.end:
            if (
                self.floor_type == NonCombatFloorType.HIDDEN_TRAP
                or self.floor_type == NonCombatFloorType.NPC_ENCOUNTER
            ):
                # Check if the user can skip the floor
                roll_result = self.handle_ability_roll(user_input)

                if (
                    roll_result == RollResult.CRITICAL_FAILURE
                    or roll_result == RollResult.FAILURE
                ):
                    # If player fails to skip the floor, go back to the ability check
                    return self.handle_ability_check(user_input, roll_result)

        return self.go_to_next_floor()

    def go_to_next_floor(self):
        #! TODO: Think about what information need to be sent back to DM
        self.end = True
        print("Going to the next floor...")
