from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.classes.ItemClasses import Rarity
from game.models.LLMProvider import LLMProvider

from game.llm_api.BackgroundRequest import (
    BackgroundRequest,
    BackgroundResponse,
    BackgroundResponseError,
)

from game.llm_api.ThemeCondenseRequest import (
    ThemeCondenseRequest,
    ThemeCondenseResponse,
)

from game.llm_api.WeaponGenerationRequest import (
    WeaponGenerationRequest,
    WeaponGenerationResponse,
)

from game.classes.NonCombatFloor import NonCombatFloor

import game.setup


class DungeonMaster:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.history: list[FloorHistory] = []

        # Request objects
        self.background_request = BackgroundRequest(self.provider)
        self.weapon_generation_request = WeaponGenerationRequest(self.provider)
        self.theme_condense_request = ThemeCondenseRequest(self.provider)

    def init_game(self, mock: bool = False):
        # Setup the backstory
        #! TODO: Handle error
        print("(System): Generating the story...")
        if mock:
            background_response = BackgroundResponse.load(
                "./test/mock/background_response.json"
            )
        else:
            background_response = self.background_request.send()

        if isinstance(background_response, BackgroundResponseError):
            print("(System): Error on generating the story. Please try again.")
            print("Error: ", background_response.message)
            return

        # Print the backstory
        print("Theme: ", background_response.theme)
        print("Player Backstory: ", background_response.player_backstory)
        print("Player Motivation: ", background_response.player_motivation)

        # Now we condense the story for later use
        #! TODO: Handle error
        print("(System): Condensing the story...")
        if mock:
            theme_condense_response = ThemeCondenseResponse.load(
                "./test/mock/theme_condense_response.json"
            )
        else:
            theme_condense_response = self.theme_condense_request.send(
                theme=background_response.theme,
                player_backstory=background_response.player_backstory,
            )

        # Store the theme for later use
        self.theme = theme_condense_response.theme

        # Setup the player
        # Get the weapon first
        #! TODO: Handle error
        print("(System): Generating the weapons...")
        if mock:
            weapon_generation_response = WeaponGenerationResponse.load(
                "./test/mock/starter_weapon.json"
            )
        else:
            weapon_generation_response = self.weapon_generation_request.send(
                theme=self.theme,
                player_backstory=theme_condense_response.player_backstory,
                rarity=Rarity.STARTER,
            )

        weapon = weapon_generation_response.to_weapon(
            rarity=Rarity.STARTER,
            base_damage=2,
        )
        print("Weapon: ", weapon)

        player = Player.create_start_player_with_random_stats(
            name="Player",
            weapon=weapon,
            description=theme_condense_response.player_backstory,
        )

        # Init game state
        self.current_floor = 1
        self.player = player

        # Print the player
        print("You are: ", self.player)

        # Print the floor
        print("You are in floor: ", self.current_floor)

        # Now initialize the floor
        self.non_combat_floor = NonCombatFloor(self.theme, self.player, self.provider)

    def start_game(self):
        self.init_game()

        #! TODO: Now I just use a while loop to simulate the game
        self.non_combat_floor.init_floor()  # First floor
        while not self.non_combat_floor.end:
            user_input = input("User: ")
            self.non_combat_floor.handle_user_input(user_input)

        print("The End!")
