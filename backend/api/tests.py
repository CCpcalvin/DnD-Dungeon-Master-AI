import os
from unittest.mock import patch

import django

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import USER_INACTIVITY_EXPIRY_INTERVAL
from .models import GameSession, GameState

User = get_user_model()


# Create your tests here.
class CustomUserTestCase(APITestCase):
    def test_user_registration_creates_last_modified(self):
        """Test that user registration creates a user with last_modified field."""
        test_time = timezone.now()
        user_data = {
            "username": "newuser",
            "password": "testpass123",
            "email": "test@example.com",
        }

        with freeze_time(test_time):
            response = self.client.post("/api/user/register", user_data)
            self.assertEqual(response.status_code, 201)

            # Check if user was created with last_modified
            user = User.objects.get(username="newuser")
            self.assertIsNotNone(user.last_modified)
            self.assertEqual(user.last_modified, test_time)

    @freeze_time("2025-01-01 12:00:00")
    def test_authentication_updates_last_modified(self):
        """Test that authentication updates the last_modified field."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        initial_last_modified = user.last_modified

        # Move time forward and authenticate
        response = self.client.post(
            "/api/user/token", {"username": "testuser", "password": "testpass123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Get the token
        token = response.data["access"]

        # Make an authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Make any authenticated request in the next frozen time
        with freeze_time("2025-01-01 12:00:15"):
            response = self.client.get("/api/get-sessions")

            # Refresh user from db
            user.refresh_from_db()

            # Check that last_modified was updated or not
            # It is expected not to update
            self.assertEqual(user.last_modified, initial_last_modified)

        # Make any authenticated request in the next frozen time
        with freeze_time("2025-01-01 12:01:15"):
            response = self.client.get("/api/get-sessions")

            # Refresh user from db
            user.refresh_from_db()

            # Check that last_modified was updated or not
            # It is expected to update
            self.assertEqual(user.last_modified, timezone.now())

    @freeze_time("2025-01-31 12:00:00")
    def test_cleanup_old_users(self):
        """Test that the cleanup_old_users command works correctly."""
        old_time = timezone.now() - USER_INACTIVITY_EXPIRY_INTERVAL - timedelta(days=1)
        with freeze_time(old_time):
            # Create old user
            old_user = User.objects.create_user(
                username="olduser", password="testpass123"
            )

            # Create superuser
            superuser = User.objects.create_superuser(
                username="adminuser", password="adminpass", email="admin@example.com"
            )

        # Create a new user
        new_user = User.objects.create_user(username="newuser", password="testpass123")

        # Verify initial state
        self.assertTrue(User.objects.filter(username="olduser").exists())
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(User.objects.filter(username="adminuser").exists())

        # Run the cleanup command
        call_command("cleanup_old_users", "--force")

        # Check results
        self.assertFalse(
            User.objects.filter(username="olduser").exists(),
            "Old user should be deleted as it was last modified before the expiry threshold",
        )
        self.assertTrue(
            User.objects.filter(username="newuser").exists(),
            "New user should be kept as it was recently active",
        )
        self.assertTrue(
            User.objects.filter(username="adminuser").exists(),
            "Superuser should be kept even if last_modified is old",
        )


class AuthUserGameSessionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def create_game_setup(self):
        """Helper method to create a game and return session_id"""
        game_data = {
            "player_name": "Test Player",
            "strength": 8,
            "dexterity": 6,
            "constitution": 7,
            "intelligence": 3,
            "wisdom": 5,
            "charisma": 1,
        }
        response = self.client.post(
            "/api/session/create-game", game_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        return response_data["session_id"]

    def test_create_game(self):
        """
        This test is for testing about the creation of game for autheroized user
        """
        # Now the user submit the POST for player creation
        response = self.client.post(
            f"/api/session/create-game",
            {
                "player_name": "Test Player",
                "strength": 6,
                "dexterity": 4,
                "constitution": 5,
                "intelligence": 5,
                "wisdom": 5,
                "charisma": 5,
            },
            format="json",
        )

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response format
        response_data = response.json()
        self.assertIn("session_id", response_data)
        self.assertIn("narrative", response_data)
        self.assertIn("state", response_data)

        session_id = response_data["session_id"]

        # Check database
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.game_state, GameState.WAITING_FOR_NEXT_FLOOR)
        self.assertTrue(hasattr(session, "player"))

        # Check PlayerInfo
        player = session.player
        self.assertEqual(player.player_name, "Test Player")
        self.assertEqual(player.strength, 6)
        self.assertEqual(player.dexterity, 4)
        self.assertEqual(player.constitution, 5)
        self.assertEqual(player.intelligence, 5)
        self.assertEqual(player.wisdom, 5)
        self.assertEqual(player.charisma, 5)

        # Check NonCombatFloorModel
        non_combat_floor_model = session.non_combat_floor_model

        # Check FloorHistoryModel
        floor_history_model = non_combat_floor_model.floor_history_model
        self.assertEqual(len(floor_history_model.content), 0)

    def test_create_game_error(self):
        # Test case 1: Missing required fields (e.g., no player_name)
        invalid_data1 = {}
        response = self.client.post(
            f"/api/session/create-game", invalid_data1, format="json"
        )
        self.assertEqual(response.status_code, 400)

        # Test case 2: Malformed JSON
        invalid_data2 = "not a valid JSON string"
        response = self.client.post(
            f"/api/session/create-game", invalid_data2, format="json"
        )
        self.assertEqual(response.status_code, 400)

        # Test case 3: Invalid data type (e.g., string for strength)
        invalid_data3 = {"player_name": "Test", "strength": "ten"}
        response = self.client.post(
            f"/api/session/create-game", invalid_data3, format="json"
        )
        self.assertEqual(response.status_code, 400)

        # Test case 4: Sum of attributes is incorrect
        incorrect_sum_data = {
            "player_name": "Test",
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }
        response = self.client.post(
            f"/api/session/create-game", incorrect_sum_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json().keys())

        # Test case 5: One attribute is below minimum
        low_attr_data = {
            "player_name": "Test",
            "strength": 0,  # The minimum is 1
            "dexterity": 5,
            "constitution": 5,
            "intelligence": 5,
            "wisdom": 5,
            "charisma": 5,
        }
        response = self.client.post(
            f"/api/session/create-game", low_attr_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json().keys())

        # Test case 6: One attribute is above maximum
        high_attr_data = {
            "player_name": "Test",
            "strength": 11,  # The maximum is 9
            "dexterity": 5,
            "constitution": 5,
            "intelligence": 5,
            "wisdom": 5,
            "charisma": 5,
        }
        response = self.client.post(
            f"/api/session/create-game", high_attr_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json().keys())

    def test_new_floor(self):
        session_id = self.create_game_setup()

        response = self.client.post(
            f"/api/session/{session_id}/new-floor", {}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # Check response format
        response_data = response.json()
        self.assertIsInstance(response_data["narrative"], str)
        self.assertIsInstance(response_data["suggested_actions"], list)
        self.assertIsInstance(response_data["state"], str)

        # Check database
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.game_state, GameState.IN_PROGRESS)
        self.assertEqual(session.current_floor, 1)

    def new_floor_setup(self, session_id):
        response = self.client.post(
            f"/api/session/{session_id}/new-floor", {}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        return response.json()

    def test_player_input(self):
        # Set up the test environment by creating a session
        session_id = self.create_game_setup()

        # Initialize a new floor
        response_data = self.new_floor_setup(session_id)

        # Assume the player use the first suggested action
        suggested_actions = response_data["suggested_actions"]
        player_action = suggested_actions[0]

        # Run test for 10 actions
        action_count = 0
        total_action = 20

        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.current_floor, 1)
        current_floor = session.current_floor

        while action_count < total_action:
            # POST to player input
            response = self.client.post(
                f"/api/session/{session_id}/player-input",
                {"action": player_action, "suggested_actions": suggested_actions},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

            # Check the response format
            response_data = response.json()
            self.assertIsInstance(response_data["state"], str)
            self.assertIsInstance(response_data["events"], list)

            match response_data["state"]:
                case "In Progress":
                    # Continue the run
                    self.assertIsInstance(response_data["suggested_actions"], list)
                    suggested_actions = response_data["suggested_actions"]
                    player_action = suggested_actions[0]

                case "Waiting for Next Floor":
                    # Test whether we can still send POST to player-input
                    response = self.client.post(
                        f"/api/session/{session_id}/player-input",
                        {
                            "action": player_action,
                            "suggested_actions": suggested_actions,
                        },
                        format="json",
                    )
                    self.assertEqual(response.status_code, 400)

                    # Start a new floor and continue the run
                    response_data = self.new_floor_setup(session_id)
                    current_floor += 1

                    suggested_actions = response_data["suggested_actions"]
                    player_action = suggested_actions[0]

                case "Completed":
                    session = GameSession.objects.get(pk=session_id)
                    self.assertEqual(session.game_state, GameState.COMPLETED)

                    # Test whether we can still send POST to player-input
                    response = self.client.post(
                        f"/api/session/{session_id}/player-input",
                        {
                            "action": player_action,
                            "suggested_actions": suggested_actions,
                        },
                        format="json",
                    )
                    self.assertEqual(response.status_code, 400)

                    break

                case _:
                    self.fail("Unexpected state: " + response_data["state"])

            action_count += 1

    def test_invalid_player_input(self):
        # Set up the test environment by creating a session
        session_id = self.create_game_setup()

        # Initialize a new floor
        response_data = self.new_floor_setup(session_id)
        suggested_actions = response_data["suggested_actions"]

        # Narrative inconsistency input
        player_action = "I take out my RPG and shoot the monster."

        # Test invalid player input
        response = self.client.post(
            f"/api/session/{session_id}/player-input",
            {"action": player_action, "suggested_actions": suggested_actions},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(
            response_data["error"],
            "Your action is not consistent with the narrative. Please re-input your action.",
        )

        # Input too short
        player_action = "Short"

        # Test invalid player input
        response = self.client.post(
            f"/api/session/{session_id}/player-input",
            {"action": player_action, "suggested_actions": suggested_actions},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(
            response_data["error"],
            "Your action is too short. Please re-input your action with more details.",
        )


class NonAuthUserGameSessionAPITest(APITestCase):
    """
    This test is for testing about the creation of session for non-authenticated user.
    """

    def test_create_session(self):
        response = self.client.post("/api/session/create-game")
        self.assertEqual(response.status_code, 401)
