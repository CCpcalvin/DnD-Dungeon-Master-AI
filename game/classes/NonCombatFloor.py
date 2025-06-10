import os, random
from typing import Union, Optional, List

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


class HandleUserInputRespond:
    """Base class for handle_user_input responses"""

    def __init__(self, messages: Optional[list[dict[str, str]]] = None):
        self.messages: list[dict[str, str]] = messages if messages is not None else []

    def add_message(self, message: dict[str, str]):
        self.messages.append(message)

    def get_messages(self):
        output_list = []
        for message in self.messages:
            if message["role"] == "Player":
                output_list.append("Player: " + message["content"])
            elif message["role"] == "System":
                output_list.append("System: " + message["content"])
            elif message["role"] == "Narrator":
                output_list.append("Narrator: " + message["content"])

        return "\n".join(output_list)


class HandleUserInputError(HandleUserInputRespond):
    """Response for error cases in user input handling"""

    def __init__(
        self, error_message: str, messages: Optional[list[dict[str, str]]] = None
    ):
        super().__init__(messages)
        self.error_message = error_message

    @classmethod
    def load(cls, response: HandleUserInputRespond, error_message: str):
        return cls(response.messages, error_message)


class HandleUserInputEnd(HandleUserInputRespond):
    """Response when the floor ends and player moves to next floor"""

    @classmethod
    def load(cls, response: HandleUserInputRespond):
        return cls(response.messages)


class HandleUserInputSuggestedAction(HandleUserInputRespond):
    """Response with suggested actions for the player"""

    def __init__(
        self,
        suggested_actions: List[str],
        messages: Optional[list[dict[str, str]]] = None,
    ):
        super().__init__(messages)
        self.suggested_actions = suggested_actions

    @classmethod
    def load(cls, response: HandleUserInputRespond, suggested_actions: List[str]):
        return cls(suggested_actions, response.messages)


class HandleUserInputDefeat(HandleUserInputRespond):
    """Response when the player is defeated"""

    @classmethod
    def load(cls, response: HandleUserInputRespond):
        return cls(response.messages)


class NonCombatFloor:
    # Config
    mocks_dir = os.path.join(GAME_PATH, "test", "mock")
    fail_penalty: float = 1 / 3
    event_length: int = 3

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
        # Create a new instance but preserve important state
        new_floor = NonCombatFloor(self.theme, self.player, self.provider)
        new_floor.penalty = 0
        new_floor.progression = Progression(self.event_length)
        new_floor.history = FloorHistory()
        return new_floor

    def init_mock(self, mock: int):
        """
        Save the response to a file, such that we do not need to regenerate it.
        It is for testing purpose.
        """
        self.current_mock_dir = os.path.join(self.mocks_dir, f"{mock}")

        if not os.path.exists(self.current_mock_dir):
            os.makedirs(self.current_mock_dir)

    def generate_floor_type(self):
        self.floor_type = random.choice(list(NonCombatFloorType))

    def generate_floor_intro(self):
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

        # Get narrative
        narrative = self.description + " " + intro_response.investigation_hook

        # Update floor history
        self.history.add_narrative(intro_response.summary)

        return intro_response, narrative

    def init_floor(self, floor_type: Optional[NonCombatFloorType] = None):
        # Init the data
        self.end = False

        # Event completion status
        self.penalty: float = 0
        self.progression = Progression(self.event_length)

        # Randomize the floor type
        if floor_type is None:
            self.generate_floor_type()
        else:
            self.floor_type = floor_type

        print("Floor type: ", self.floor_type.value)

        print("(System): Generating floor description...")
        #! TODO: Error handling
        # Get the floor description and investigation hook
        intro_response, narrative = self.generate_floor_intro()
        print(narrative)

        print("What do you want to do?")
        for i, action in enumerate(intro_response.suggested_actions):
            print(f"{i + 1}. {action}")
        print(f"{i + 2}. Go to the next floor.")
        print(f"{i + 3}. Write your own action.")

        return intro_response.suggested_actions

    def handle_user_input(
        self, user_input: str, suggested_actions: list[str], verbose: bool = True
    ) -> HandleUserInputRespond:
        output = HandleUserInputRespond()

        if verbose:
            print("(System): Classifying your action...")

        # Do a simple string check
        if len(user_input.strip()) < 10:
            if verbose:
                print(
                    "(System): Your action is too short. Please re-input your action with more details."
                )

            return HandleUserInputError.load(
                output,
                "Your action is too short. Please re-input your action with more details.",
            )

        formatted_user_input = user_input.lower().strip()
        for action in suggested_actions:
            # If the user input is a part of the suggested action, handle it as an ability check directly
            if formatted_user_input in action.lower().strip():
                output.add_message({"role": "Player", "content": user_input})
                return self.handle_ability_check(user_input, output, verbose=verbose)

        # If the user input is "go to the next floor", skip the floor
        if formatted_user_input in "Go to the next floor.".lower().strip():
            output.add_message({"role": "Player", "content": user_input})
            return self.skip_floor(user_input, output, verbose=verbose)

        #! TODO: Error handling
        classify_action_response = self.classify_action_request.send(user_input)

        if classify_action_response.narrative_consistency is False:
            if verbose:
                print(
                    "(System): Your action is not consistent with the narrative. Please re-input your action"
                )
            return HandleUserInputError.load(
                output,
                "Your action is not consistent with the narrative. Please re-input your action",
            )

        if classify_action_response.action_type == "unknown":
            if verbose:
                print(
                    "(System): System cannot classify your action. Please re-input your action"
                )
            return HandleUserInputError.load(
                output,
                "System cannot classify your action. Please re-input your action",
            )

        output.add_message({"role": "Player", "content": user_input})
        if classify_action_response.action_type == "ability_check":
            return self.handle_ability_check(user_input, output, verbose=verbose)

        #! TODO: Not yet implemented
        elif classify_action_response.action_type == "use_item":
            return self.handle_use_item()

        elif classify_action_response.action_type == "go_to_next_floor":
            return self.skip_floor(user_input, output)

    def handle_ability_roll(
        self, user_input: str, output: HandleUserInputRespond, verbose: bool = True
    ):
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
        feedback = f"(System): Score: {score} = {roll} (Roll) + {self.player.get_attribute(ability_check_response.attribute)} ({ability_check_response.attribute}). The DC is {ability_check_response.difficulty_class}. It is {roll_result.value}."
        if verbose:
            print(feedback)

        output.add_message({"role": "System", "content": feedback})

        return roll_result

    def handle_ability_check(
        self,
        user_input: str,
        output: HandleUserInputRespond,
        by_pass_roll_result: Optional[RollResult] = None,
        verbose: bool = True,
    ) -> HandleUserInputRespond:
        if by_pass_roll_result is None:
            roll_result = self.handle_ability_roll(user_input, output, verbose=verbose)
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

        # Add to the history
        self.history.add_player_actions(user_input, roll_result)

        return self.handle_resolution(story_extend_response, output, verbose=verbose)

    #! TODO here
    def handle_use_item(self, verbose: bool = True) -> HandleUserInputRespond:
        if self.player.num_of_items() == 0:
            if verbose:
                print(
                    "(System): I think you are trying to use an item, but you have no items in your inventory. Please re-input your action"
                )
            return HandleUserInputError(
                "I think you are trying to use an item, but you have no items in your inventory. Please re-input your action"
            )

        if verbose:
            item_index = int(
                input("(System): Please input the item index you want to use: ")
            )
            user_input = input("(System): How do you use the item?\n")
        else:
            # Default values when not in verbose mode
            item_index = 0
            user_input = "Use item"

        return self.use_item_resolution(item_index, user_input)

    #! TODO here
    def use_item_resolution(
        self, item_index: int, user_input: str, verbose: bool = True
    ):
        if verbose:
            print("(System): Resolving item usage...")
        #! TODO: Error handling
        item_use_resolution_response = self.item_use_resolution_request.send(
            item_to_use=self.player.inventory[item_index],
            user_input=user_input,
            floor_type=self.floor_type,
        )

        if item_use_resolution_response.is_item_consumed:
            self.player.inventory.pop(item_index)

        return self.handle_resolution(item_use_resolution_response, verbose=verbose)

    def handle_reward(
        self,
        reward_type: str,
        recent_history: str,
        output: HandleUserInputRespond,
        verbose: bool = True,
    ):
        if reward_type == "heal":
            heal_amount = random.randint(1, 4)
            feedback = f"(System): You are healed for {heal_amount} health."
            output.add_message({"role": "System", "content": feedback})
            if verbose:
                print(feedback)

            self.player.update_health(heal_amount, verbose=verbose)

        elif reward_type == "max_health_increase":
            increase_amount = 1
            feedback = (
                f"(System): Your maximum health is increased by {increase_amount}."
            )
            output.add_message({"role": "System", "content": feedback})
            if verbose:
                print(feedback)

            self.player.max_health += increase_amount

        elif reward_type == "attribute_increase":
            attribute_reward_respond = self.attribute_reward_request.send(
                recent_history=recent_history
            )
            self.player.update_attribute(attribute_reward_respond.attribute, 1)
            feedback = f"(System): Your {attribute_reward_respond.attribute} is increased by 1."
            output.add_message({"role": "System", "content": feedback})
            if verbose:
                print(feedback)

        elif verbose:
            print("(System): Unknown reward type. No reward given.")

    def handle_resolution(
        self,
        response: Union[
            ItemUseResolutionResponseModel, AbilityCheckResolutionResponseModel
        ],
        output: HandleUserInputRespond,
        verbose: bool = True,
    ) -> HandleUserInputRespond:

        # Print the story if in verbose mode
        output.add_message({"role": "Narrator", "content": response.narrative})
        if verbose:
            print(response.narrative)

        # Update the player's health
        #! TODO: Check player health! We need special treatment when player is dead here
        self.player.update_health(response.health_change, verbose=verbose)

        # Write to the output if we have health change
        if response.health_change > 0:
            output.add_message(
                {
                    "role": "System",
                    "content": f"You are healed for {response.health_change} health.",
                }
            )

        elif response.health_change < 0:
            output.add_message(
                {
                    "role": "System",
                    "content": f"You are damaged for {response.health_change} health.",
                }
            )

        # Add the user input and story extension to the history
        self.history.add_narrative(response.summary)

        # Check if the event is ended
        #! TODO:
        if self.player.is_defeated():
            if verbose:
                print("(System): You are defeated.")

            return HandleUserInputDefeat.load(output)

        if self.progression.is_failed():
            if verbose:
                print("(System): The event is ended with failure.")
            return self.go_to_next_floor(output, verbose=verbose)

        elif self.progression.is_completed():
            if verbose:
                print("(System): The event is completed successfully.")

            classify_reward_type_respond = self.classify_reward_type_request.send(
                recent_history=response.narrative,
            )

            # Handle reward
            self.handle_reward(
                classify_reward_type_respond.reward_type,
                recent_history=response.narrative,
                output=output,
                verbose=verbose,
            )

            return self.go_to_next_floor(output, verbose=verbose)

        else:
            # Suggest some actions for the player to take
            if verbose:
                print("(System): Suggesting actions...")

            #! TODO: Error handling
            suggest_action_response = self.suggest_action_request.send(
                recent_history=response.narrative,
            )

            if verbose:
                # Print the suggested actions
                print("(System): Suggested actions:")
                for i, action in enumerate(suggest_action_response.suggested_actions):
                    print(f"{i + 1}. {action}")

                print(f"{i + 2}. Write your own action.")

            return HandleUserInputSuggestedAction.load(
                output, suggest_action_response.suggested_actions
            )

    def skip_floor(
        self, user_input: str, output: HandleUserInputRespond, verbose: bool = True
    ) -> HandleUserInputRespond:
        if not self.end:
            if (
                self.floor_type == NonCombatFloorType.HIDDEN_TRAP
                or self.floor_type == NonCombatFloorType.NPC_ENCOUNTER
            ):
                # Check if the user can skip the floor
                roll_result = self.handle_ability_roll(
                    user_input, output, verbose=verbose
                )

                if (
                    roll_result == RollResult.CRITICAL_FAILURE
                    or roll_result == RollResult.FAILURE
                ):
                    # If player fails to skip the floor, go back to the ability check
                    return self.handle_ability_check(
                        user_input, roll_result, output, verbose=verbose
                    )

        return self.go_to_next_floor(output, verbose=verbose)

    def go_to_next_floor(
        self, output: HandleUserInputRespond, verbose: bool = True
    ) -> HandleUserInputEnd:
        #! TODO: Think about what information need to be sent back to DM
        self.end = True

        if verbose:
            print("Going to the next floor...")

        return HandleUserInputEnd.load(output)
