from game.classes.LLMModel import LLMModel
from game.classes.NonCombatFloorType import NonCombatFloorType
from game.llm_api.NonCombatFloorIntroRequest import (
    NonCombatFloorIntroRequest,
    NonCombatFloorIntroResponse,
)
from game.classes.EntityClasses import Player

import random


class NonCombatFloor:
    def __init__(self, theme: str, player: Player, model: LLMModel):
        self.theme = theme
        self.player = player
        self.model = model

        # Request object
        self.intro_request = NonCombatFloorIntroRequest(self.model)
    
    def get_intro_response(self):
        return self.intro_request.send(
            theme=self.theme,
            player_description=self.player.description,
            floor_type=self.floor_type,
        )

    def init_floor(self, mock: bool = False):
        # Randomize the floor type
        self.floor_type = random.choice(list(NonCombatFloorType))

        #! TODO: Error handling
        # Get the floor description and investigation hook
        if mock:
            intro_response = NonCombatFloorIntroResponse.load(
                "./test/mock/non_combat_floor_intro_response.json"
            )
        else:
            intro_response = self.get_intro_response()

        # Set the description
        self.description = intro_response.description

        print(self.description)
        print(intro_response.investigation_hook)

        print("What do you want to do?")
        for i, action in enumerate(intro_response.suggested_actions):
            print(f"{i + 1}. {action}")
        print(f"{i + 2}. Go to the next floor.")
        print(f"{i + 3}. Custom.")

    def handle_user_input(self, user_input: str):
        if user_input == i + 2:
            return self.floor_type
        elif user_input == i + 3:
            return "custom"
        else:
            return intro_response.suggested_actions[user_input - 1]
