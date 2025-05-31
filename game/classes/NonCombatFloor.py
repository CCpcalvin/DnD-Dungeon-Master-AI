from game.classes.LLMModel import LLMModel
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.llm_api.NonCombatFloorIntroRequest import (
    NonCombatFloorIntroRequest,
    NonCombatFloorIntroResponse,
)
from game.llm_api.ClassifyNonCombatActionRequest import (
    ClassifyNonCombatActionRequest,
    ClassifyNonCombatActionResponse,
    ClassifyNonCombatActionResponseSuccess,
    ClassifyNonCombatActionResponseError,
)
from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

import random


class NonCombatFloor:
    def __init__(self, theme: str, player: Player, model: LLMModel):
        self.theme = theme
        self.player = player
        self.model = model

        # History
        self.history: FloorHistory = FloorHistory()

        # Request objects
        self.intro_request = NonCombatFloorIntroRequest(
            self.model, theme, player.description
        )
        self.classify_action_request = ClassifyNonCombatActionRequest(
            self.model,
            theme,
            player,
            self.history,
        )

    def reload(self):
        return NonCombatFloor(self.theme, self.player, self.model)

    def init_floor(self, mock: bool = False):
        # Randomize the floor type
        self.floor_type = random.choice(list(NonCombatFloorType))

        print("(System): Generating floor description...")
        #! TODO: Error handling
        # Get the floor description and investigation hook
        if mock:
            intro_response = NonCombatFloorIntroResponse.load(
                "./test/mock/non_combat_floor_intro_response.json"
            )
        else:
            intro_response = self.intro_request.send(self.floor_type)

        # Set the description
        self.description = intro_response.description

        narrative = self.description + " " + intro_response.investigation_hook
        print(narrative)

        self.history.add_narrative(intro_response.summary)

        print("What do you want to do?")
        for i, action in enumerate(intro_response.suggested_actions):
            print(f"{i + 1}. {action}")
        print(f"{i + 2}. Go to the next floor.")
        print(f"{i + 3}. Custom.")

    def handle_user_input(self, user_input: str):
        #! TODO: Error handling
        print("(System): Classifying your action...")
        classify_action_response = self.classify_action_request.send(user_input)

        if isinstance(classify_action_response, ClassifyNonCombatActionResponseSuccess):
            if classify_action_response.action_type == "ability_check":
                self.handle_ability_check(user_input)
            elif classify_action_response.action_type == "use_item":
                pass
            elif classify_action_response.action_type == "go_to_next_floor":
                self.go_to_next_floor()

        elif isinstance(
            classify_action_response,
            ClassifyNonCombatActionResponseNarrativeConsistencyError,
        ):
            print(
                "(System): Your action is not consistent with the narrative. Please re-input your action"
            )
        elif isinstance(
            classify_action_response,
            ClassifyNonCombatActionResponseUnknownError,
        ):
            print(
                "(System): We cannot classify your action. Please re-input your action"
            )
        elif isinstance(classify_action_response, ClassifyNonCombatActionResponseError):
            print(
                "(System): Error on classifying your action. Please re-input your action"
            )

    def handle_ability_check(self, user_input: str):
        pass

    def go_to_next_floor(self):
        pass

    def handle_use_item(self, user_input: str):
        pass
