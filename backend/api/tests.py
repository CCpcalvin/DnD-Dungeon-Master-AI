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
        response = self.client.post("/api/session/new/", {}, format="json")
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        response_data = response.json()
        session_id = response_data["session_id"]
        narrative = response_data["narrative"]
        # print("Narrative:", narrative)

        # Check database state
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.current_floor, 1)
        self.assertEqual(session.game_state, GameState.PLAYER_CREATION)

        # Check GameEvent
        event = GameEvent.objects.get(session=session)
        self.assertEqual(event.content, narrative)

    def test_create_player(self):
        """
        This test is for testing about the creation of session for autheroized user
        """
        # print("\nRunning Create Player Test...")
        # Simulate user for creating the session
        response = self.client.post("/api/session/new/", {}, format="json")
        response_data = response.json()
        session_id = response_data["session_id"]
        narrative = response_data["narrative"]
        # print("Narrative:", narrative)

        # Now the user submit the POST for player creation
        response = self.client.post(
            f"/api/session/{session_id}/create-player/",
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
        self.assertIsInstance(response_data["narrative"], str)
        self.assertIsInstance(response_data["suggested_actions"], list)

        # print("Narrative:", response_data["narrative"])
        # print("Suggested Actions:", response_data["suggested_actions"])

        # Check database
        session = GameSession.objects.get(pk=session_id)
        self.assertEqual(session.game_state, GameState.IN_PROGRESS)

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
        self.assertEqual(len(floor_history_model.content), 1)


class NonAuthUserGameSessionAPITest(APITestCase):
    def test_create_session(self):
        """
        This test is for testing about the creation of session for non-autheroized user.
        """
        # Clear any existing credentials to simulate a logged-out user
        self.client.credentials()

        # Simulate user submitting a POST to the session_new endpoint
        response = self.client.post("/api/session/new/", {}, format="json")
        self.assertEqual(response.status_code, 401)
