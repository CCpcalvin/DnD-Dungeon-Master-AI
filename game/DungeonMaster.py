from game.Const import GAME_PATH
from game.models.LLMProvider import LLMProvider

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory

from game.llm_api.BackgroundRequest import BackgroundRequest, BackgroundResponseModel
from game.llm_api.ThemeCondenseRequest import (
    ThemeCondenseRequest,
    ThemeCondenseResponseModel,
)

# from game.llm_api.WeaponGenerationRequest import (
#     WeaponGenerationRequest,
#     WeaponGenerationResponse,
# )

from game.classes.NonCombatFloor import NonCombatFloor

import os

from typing import Optional


class DungeonMaster:
    mocks_dir = os.path.join(GAME_PATH, "test", "mock")

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.history: list[FloorHistory] = []

        # Request objects
        self.background_request = BackgroundRequest(self.provider)
        self.theme_condense_request = ThemeCondenseRequest(self.provider)
        # self.weapon_generation_request = WeaponGenerationRequest(self.provider)

    def init_mock(self, mock: int):
        """
        Save the response to a file, such that we do not need to regenerate it.
        It is for testing purpose.
        """
        self.current_mock_dir = os.path.join(self.mocks_dir, f"{mock}")

        if not os.path.exists(self.current_mock_dir):
            os.makedirs(self.current_mock_dir)

    def check_mock_exists(self, file_name: str) -> bool:
        """
        Check if the mock file exists.
        """
        file_path = os.path.join(self.current_mock_dir, file_name)
        return os.path.exists(file_path)

    def init_game(self, mock: Optional[int] = None):
        if mock is not None:
            self.init_mock(mock)

        #! TODO: Error handling
        # Setup the backstory
        print("(System): Generating the story...")
        background_response: BackgroundResponseModel = (
            self.background_request.send_and_save_to_mock(
                mocks_dir=self.mocks_dir,
                save_file_name="background_response.json",
                mock=mock,
            )
        )

        # Print the backstory
        print("Theme: ", background_response.theme)
        print("Player Backstory: ", background_response.player_backstory)
        print("Player Motivation: ", background_response.player_motivation)

        # Now we condense the story for later use
        #! TODO: Handle error
        print("(System): Condensing the story...")
        theme_condense_response: ThemeCondenseResponseModel = (
            self.theme_condense_request.send_and_save_to_mock(
                mocks_dir=self.mocks_dir,
                save_file_name="theme_condense_response.json",
                mock=mock,
                theme=background_response.theme,
                player_backstory=background_response.player_backstory,
            )
        )

        # Store the theme for later use
        self.theme = theme_condense_response.theme

        # Setup the player
        # Get the weapon first
        #! TODO: Later handle combat
        #! TODO: Handle error
        # print("(System): Generating the weapons...")
        # if mock:
        #     weapon_generation_response = WeaponGenerationResponse.load(
        #         "./test/mock/starter_weapon.json"
        #     )
        # else:
        #     weapon_generation_response = self.weapon_generation_request.send(
        #         theme=self.theme,
        #         player_backstory=theme_condense_response.player_backstory,
        #         rarity=Rarity.STARTER,
        #     )

        # weapon = weapon_generation_response.to_weapon(
        #     rarity=Rarity.STARTER,
        #     base_damage=2,
        # )
        # print("Weapon: ", weapon)

        player = Player.create_start_player_with_random_stats(
            name="Player",
            # weapon=weapon,
            description=theme_condense_response.player_backstory,
        )

        # Init game state
        self.current_floor = 1
        self.player = player

        # Print the player
        print("You are: ", self.player)

        # Now initialize the floor
        self.non_combat_floor = NonCombatFloor(self.theme, self.player, self.provider)

    def start_game(self):
        self.init_game()
        self.current_floor = 1

        #! TODO: Now I just use a while loop to simulate the game
        while True:
            print(f"\n--- Starting Floor {self.current_floor} ---")

            self.non_combat_floor = self.non_combat_floor.reload()
            suggested_actions = self.non_combat_floor.init_floor()  # First floor
            while not self.non_combat_floor.end:
                user_input = input("User: ")
                output = self.non_combat_floor.handle_user_input(user_input, suggested_actions)
                if output is not None:
                    suggested_actions = output
            
            self.current_floor += 1

        print("The End!")
