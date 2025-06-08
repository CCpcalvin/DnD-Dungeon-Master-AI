from django.db import models
from django.contrib.auth.models import User  # Input Users model

from game.classes.EntityClasses import Player
from game.classes.FloorHistory import FloorHistory
from game.classes.NonCombatFloor import NonCombatFloor
from game.classes.Progression import Progression
from game.models.LLMProvider import ollama
from game.DungeonMaster import DungeonMaster


class GameState(models.TextChoices):
    PLAYER_CREATION = "Player Creation"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class GameSession(models.Model):
    """
    Model to represent a game session.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who owns the session
    created_at = models.DateTimeField(auto_now_add=True)
    theme = models.CharField(
        max_length=255, blank=True, null=True
    )  # Theme of the game session
    current_floor = models.IntegerField(default=1)  # Current floor in the game session
    game_state = models.CharField(
        max_length=20,
        choices=GameState.choices,
        default=GameState.IN_PROGRESS,
    )  # State of the game session

    def __str__(self):
        return f"{self.pk} by {self.user.username} at {self.created_at}"

    def load_dm(self):
        # Create DM object
        dm = DungeonMaster(ollama())

        # Set class attributes
        dm.theme = self.theme
        dm.current_floor = self.current_floor
        dm.player = self.player.load_player()

        # Load floor
        floor = self.non_combat_floor_model.load_non_combat_floor(dm.theme, dm.player)
        dm.non_combat_floor = floor

        return dm

    def save_dm(self, dm: DungeonMaster):
        self.current_floor = dm.current_floor
        self.player.save_player(dm.player)

        self.non_combat_floor_model.save_non_combat_floor(dm.non_combat_floor)
        self.save()


class GameEvent(models.Model):
    """
    Stores a single event or story segment in a game session.
    """

    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="events"
    )
    content = models.TextField()  # The story segment
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event {self.pk} for session {self.session.pk} at {self.created_at}"


class PlayerInfo(models.Model):
    """
    Represents an attribute of a player in a game session.
    """

    session = models.OneToOneField(
        GameSession, on_delete=models.CASCADE, related_name="player"
    )
    player_name = models.CharField(
        max_length=50, blank=True, null=True
    )  # Name of the player
    description = models.TextField()  # Description of the player
    current_health = models.IntegerField(default=10)  # Current health of the player
    max_health = models.IntegerField(default=10)  # Maximum health of the player
    strength = models.IntegerField(blank=True, null=True)  # Strength attribute
    dexterity = models.IntegerField(blank=True, null=True)  # Dexterity attribute
    constitution = models.IntegerField(blank=True, null=True)  # Constitution attribute
    intelligence = models.IntegerField(blank=True, null=True)  # Intelligence attribute
    wisdom = models.IntegerField(blank=True, null=True)  # Wisdom attribute
    charisma = models.IntegerField(blank=True, null=True)  # Charisma attribute

    def __str__(self):
        return f"{self.player_name} for session {self.session.pk}"

    def load_player(self):
        return Player(
            name=self.player_name,
            description=self.description,
            inventory=[],
            current_health=self.current_health,
            max_health=self.max_health,
            strength=self.strength,
            dexterity=self.dexterity,
            constitution=self.constitution,
            intelligence=self.intelligence,
            wisdom=self.wisdom,
            charisma=self.charisma,
        )

    def save_player(self, player: Player):
        self.current_health = player.current_health
        self.max_health = player.max_health
        self.strength = player.strength
        self.dexterity = player.dexterity
        self.constitution = player.constitution
        self.intelligence = player.intelligence
        self.wisdom = player.wisdom
        self.charisma = player.charisma
        self.save()


class FloorHistoryModel(models.Model):
    session = models.OneToOneField(
        GameSession, on_delete=models.CASCADE, related_name="floor_history"
    )
    content = models.JSONField()

    def __str__(self):
        return f"Floor history for session {self.session.pk}"

    def load_floor_history(self) -> FloorHistory:
        return FloorHistory.load(content=self.content)

    def save_floor_history(self, floor_history: FloorHistory):
        self.content = floor_history.content
        self.save()


class NonCombatFloorTypeModel(models.TextChoices):
    TREASURE = "Treasure"
    TREASURE_WITH_TRAP = "Treasure with Trap"
    HIDDEN_TRAP = "Hidden Trap"
    NPC_ENCOUNTER = "NPC Encounter"


class NonCombatFloorModel(models.Model):
    session = models.OneToOneField(
        GameSession, on_delete=models.CASCADE, related_name="non_combat_floor_model"
    )
    floor_history_model = models.OneToOneField(
        FloorHistoryModel,
        on_delete=models.CASCADE,
        related_name="non_combat_floor_model",
    )

    # Floor attribute
    floor_type = models.CharField(
        max_length=20,
        choices=NonCombatFloorTypeModel.choices,
        default=NonCombatFloorTypeModel.TREASURE,
    )
    description = models.TextField(null=True, blank=True)

    # Event completion status
    penalty = models.FloatField(default=0)
    completion_rate = models.IntegerField(default=0)

    def __str__(self):
        return f"Non combat floor for session {self.session.pk}"

    def load_non_combat_floor(self, theme: str, player: Player):
        # Create NonCombatFloor object
        floor = NonCombatFloor(theme, player, ollama())

        # Load floor history
        floor_history = self.floor_history_model.load_floor_history()

        # Set class attributes
        floor.history = floor_history
        floor.floor_type = NonCombatFloorTypeModel(self.floor_type)
        floor.penalty = self.penalty
        floor.progression = Progression.load(self.completion_rate, floor.event_length)

        return floor

    def save_non_combat_floor(self, non_combat_floor: NonCombatFloor):
        self.floor_history_model.save_floor_history(non_combat_floor.history)

        self.floor_type = non_combat_floor.floor_type.value
        self.penalty = non_combat_floor.penalty
        self.completion_rate = non_combat_floor.progression.completion_rate
        self.save()
