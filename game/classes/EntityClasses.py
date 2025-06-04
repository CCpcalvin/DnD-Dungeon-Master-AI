from dataclasses import dataclass, asdict
from game.classes.ItemClasses import Item, Weapon

import random, json


@dataclass
class Entity:
    description: str
    current_health: int
    max_health: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


@dataclass
class Player(Entity):
    name: str
    #!: TODO: Later handle combat
    # weapon: Weapon
    inventory: list[Item]

    min_per_attr: int = 1  # Ensure no stat is zero
    max_per_attr: int = 9

    start_health: int = 10

    @classmethod
    def create_start_player_with_random_stats(cls, name: str, description: str):
        """
        Create a new Player with randomized stats that sum to 35,
        with each stat having a maximum of 9.
        """
        # Define the attributes we want to randomize
        attributes = [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        total_points = 30

        # Start with minimum values
        stats = {attr: cls.min_per_attr for attr in attributes}
        remaining_points = total_points - (cls.min_per_attr * len(attributes))

        # Distribute remaining points randomly
        while remaining_points > 0:
            # Pick a random attribute to increase
            attr = random.choice(attributes)
            # Only increase if below max
            if stats[attr] < cls.max_per_attr:
                stats[attr] += 1
                remaining_points -= 1

        # Create and return the player
        return cls(
            name=name,
            # weapon=weapon,
            description=description,
            inventory=[],
            strength=stats["strength"],
            dexterity=stats["dexterity"],
            constitution=stats["constitution"],
            intelligence=stats["intelligence"],
            wisdom=stats["wisdom"],
            charisma=stats["charisma"],
            current_health=cls.start_health,
            max_health=cls.start_health,
        )

    def inventory_prompt(self) -> str:
        if len(self.inventory) == 0:
            return "No items in inventory"

        to_print: list[str] = []
        for item in self.inventory:
            to_print.append(item.name)

        return str(to_print)

    def inventory_full_prompt(self) -> str:
        if len(self.inventory) == 0:
            return "No items in inventory"

        to_print: list[str] = []
        for item in self.inventory:
            to_print.append(json.dumps(asdict(item)))

        return str(to_print)

    def get_attribute(self, attribute: str) -> int:
        return getattr(self, attribute)

    def update_health(self, health_change: int):
        self.current_health += health_change


@dataclass
class Enemy(Entity):
    normal_damage: int
