import os
import django

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from .models import GameState, GameSession, GameEvent


# Create your tests here.
class AuthUserGameSessionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_create_session(self):
        """
        This test is for testing about the creation of session for autheroized user.
        """
        # print("\nRunning Create Session Test...")

        # Simulate user submitting a POST to the session_new endpoint
        response = self.client.post("/api/session/new", {}, format="json")
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        response_data = response.json()
        session_id = response_data["session_id"]
        narrative = response_data["narrative"]
        # print("Narrative:", narrative)

        # Check database state
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.current_floor, 0)
        self.assertEqual(session.game_state, GameState.PLAYER_CREATION)

        # Check GameEvent
        event = GameEvent.objects.get(session=session)
        self.assertEqual(event.content, narrative)

    def create_player_setup(self):
        response = self.client.post("/api/session/new", {}, format="json")
        response_data = response.json()
        session_id = response_data["session_id"]
        narrative = response_data["narrative"]
        # print("Narrative:", narrative)

        return session_id

    def new_floor_setup(self, session_id, current_floor: int):
        response = self.client.post(
            f"/api/session/{session_id}/new-floor", {}, format="json"
        )

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response format
        response_data = response.json()
        self.assertIsInstance(response_data["narrative"], str)
        self.assertIsInstance(response_data["suggested_actions"], list)

        # Check the game state
        session = GameSession.objects.get(pk=session_id)
        session.refresh_from_db()
        self.assertEqual(session.game_state, GameState.IN_PROGRESS)

        # Check current floor
        self.assertEqual(session.current_floor, current_floor + 1)

        # print("Narrative:", response_data["narrative"])
        # print("Suggested Actions:", response_data["suggested_actions"])

        # Check NonCombatFloorModel
        non_combat_floor_model = session.non_combat_floor_model

        # Check FloorHistoryModel
        floor_history_model = non_combat_floor_model.floor_history_model

        self.assertEqual(len(floor_history_model.content), 1)

        return response_data

    def test_create_player(self):
        """
        This test is for testing about the creation of session for autheroized user
        """
        # print("\nRunning Create Player Test...")
        # Simulate user for creating the session
        session_id = self.create_player_setup()

        # Now the user submit the POST for player creation
        response = self.client.post(
            f"/api/session/{session_id}/create-player",
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

        # Check database
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.game_state, GameState.WAITING_FOR_NEXT_FLOOR)

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

        self.new_floor_setup(session_id, 0)

    def test_create_player_error(self):
        # Get the session_id by calling create_player_setup
        session_id = self.create_player_setup()

        # Test case 1: Missing required fields (e.g., no player_name)
        invalid_data1 = {}
        response = self.client.post(
            f"/api/session/{session_id}/create-player", invalid_data1, format="json"
        )
        self.assertEqual(response.status_code, 400)

        # Test case 2: Malformed JSON
        invalid_data2 = "not a valid JSON string"
        response = self.client.post(
            f"/api/session/{session_id}/create-player", invalid_data2, format="json"
        )
        self.assertEqual(response.status_code, 400)

        # Test case 3: Invalid data type (e.g., string for strength)
        invalid_data3 = {"player_name": "Test", "strength": "ten"}
        response = self.client.post(
            f"/api/session/{session_id}/create-player", invalid_data3, format="json"
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
            f"/api/session/{session_id}/create-player",
            incorrect_sum_data,
            format="json",
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
            f"/api/session/{session_id}/create-player", low_attr_data, format="json"
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
            f"/api/session/{session_id}/create-player", high_attr_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json().keys())

    def test_player_input(self):
        # Set up the test environment by creating a session
        session_id = self.create_player_setup()

        # Create a player
        response = self.client.post(
            f"/api/session/{session_id}/create-player",
            {
                "player_name": "Test Player",
                "strength": 8,
                "dexterity": 6,
                "constitution": 7,
                "intelligence": 3,
                "wisdom": 5,
                "charisma": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        # Initialize a new floor
        response_data = self.new_floor_setup(session_id, 0)

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
                    response_data = self.new_floor_setup(session_id, current_floor)
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
        session_id = self.create_player_setup()

        # Create a player
        response = self.client.post(
            f"/api/session/{session_id}/create-player",
            {
                "player_name": "Test Player",
                "strength": 8,
                "dexterity": 6,
                "constitution": 7,
                "intelligence": 3,
                "wisdom": 5,
                "charisma": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        # Initialize a new floor
        response_data = self.new_floor_setup(session_id, 0)
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

        # Input too short
        player_action = "Short"

        # Test invalid player input
        response = self.client.post(
            f"/api/session/{session_id}/player-input",
            {"action": player_action, "suggested_actions": suggested_actions},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class NonAuthUserGameSessionAPITest(APITestCase):
    def test_create_session(self):
        """
        This test is for testing about the creation of session for non-autheroized user.
        """
        # Simulate user submitting a POST to the session_new endpoint
        response = self.client.post("/api/session/new", {}, format="json")
        self.assertEqual(response.status_code, 401)
