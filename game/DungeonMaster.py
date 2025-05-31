from game.classes.LLMModel import LLMModel
from game.classes.FloorHistory import FloorHistory
from game.classes.EntityClasses import Player
from game.classes.ItemClasses import Rarity

from game.llm_api.BackgroundRequest import BackgroundRequest, BackgroundResponse
from game.llm_api.WeaponGenerationRequest import (
    WeaponGenerationRequest,
    WeaponGenerationResponse,
)
from game.llm_api.ThemeCondenseRequest import (
    ThemeCondenseRequest,
    ThemeCondenseResponse,
)


class DungeonMaster:
    def __init__(self, model: LLMModel):
        self.model = model
        self.history: list[FloorHistory] = []

        # Request objects
        self.background_request = BackgroundRequest(self.model)
        self.weapon_generation_request = WeaponGenerationRequest(self.model)
        self.theme_condense_request = ThemeCondenseRequest(self.model)

    def start_game(self, mock: bool = False):
        # Setup the backstory
        #! TODO: Handle error
        print("(System): Generating the story...")
        if mock:
            background_response = BackgroundResponse.load(
                "./test/mock/background_response.json"
            )
        else:
            background_response = self.background_request.send()

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
