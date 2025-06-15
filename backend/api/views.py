from game.DungeonMaster import DungeonMaster
from game.classes.EntityClasses import Player
from game.models.LLMProvider import ollama
from game.classes.NonCombatFloor import (
    HandleUserInputError,
    HandleUserInputEnd,
    HandleUserInputDefeat,
    HandleUserInputSuggestedAction,
)

from django.http import HttpResponse, JsonResponse, HttpRequest

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from .serializers import UserSerializer

from django.contrib.auth.models import User
from .models import (
    GameState,
    GameSession,
    Role,
    GameEvent,
    PlayerInfo,
    FloorHistoryModel,
    NonCombatFloorModel,
)

import json


# Create your views here.
def index(request: HttpRequest):
    """
    Render the index page.
    """
    return HttpResponse("dnd game master is running.")


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_game(request: HttpRequest):
    try:
        # Parse request data
        data = json.loads(request.body)

        if not isinstance(data, dict):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Validate required fields
        required_fields = [
            "player_name",
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]

        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            player_name = str(data["player_name"])
            strength = int(data["strength"])
            dexterity = int(data["dexterity"])
            constitution = int(data["constitution"])
            intelligence = int(data["intelligence"])
            wisdom = int(data["wisdom"])
            charisma = int(data["charisma"])

        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Validate attributes
        attributes = [strength, dexterity, constitution, intelligence, wisdom, charisma]
        if sum(attributes) > Player.start_attribute_sum:
            return JsonResponse(
                {"error": f"Stats sum to more than {Player.start_attribute_sum}"},
                status=400,
            )

        if any(attr < Player.min_per_attr for attr in attributes):
            return JsonResponse(
                {"error": f"Stats must be at least {Player.min_per_attr}"}, status=400
            )

        if any(attr > Player.max_per_attr for attr in attributes):
            return JsonResponse(
                {"error": f"Stats must be at most {Player.max_per_attr}"}, status=400
            )

        # Create the session
        session = GameSession.objects.create(
            user=request.user,
            theme="Dungeon Adventure",  # This will be updated by the LLM
            game_state=GameState.WAITING_FOR_NEXT_FLOOR,
        )

        # Initialize DM and generate theme
        dm = DungeonMaster(provider=ollama())
        background_response = dm.generate_theme()
        condensed_response = dm.condense_theme(
            theme=background_response.theme,
            player_backstory=background_response.player_backstory,
        )

        # Update session with theme
        session.theme = condensed_response.theme
        session.save()

        # Create GameEvent for the narrative
        combined_content = (
            f"{background_response.theme} "
            f"{background_response.player_backstory} "
            f"{background_response.player_motivation}"
        )
        GameEvent.objects.create(
            session=session, role=Role.NARRATOR, content=combined_content
        )

        # Create player with all attributes
        PlayerInfo.objects.create(
            session=session,
            player_name=player_name,
            description=condensed_response.player_backstory,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            current_health=Player.start_health,
            max_health=Player.start_health,
        )

        # Initialize game objects
        floor_history_model = FloorHistoryModel.objects.create(
            session=session, content=[]
        )
        NonCombatFloorModel.objects.create(
            session=session, floor_history_model=floor_history_model
        )

        return JsonResponse(
            {
                "session_id": session.pk,
                "narrative": combined_content,
                "state": session.game_state,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_floor(request: HttpRequest, session_id: int):
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)

    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    if session.game_state != GameState.WAITING_FOR_NEXT_FLOOR:
        return JsonResponse(
            {"error": "Cannot create new floor in this state"}, status=400
        )

    # Load the DM
    dm = session.load_dm()

    # Now we start the floor
    # Reload the floor and assign the new instance back to dm
    dm.current_floor += 1
    dm.non_combat_floor = dm.non_combat_floor.reload()
    dm.non_combat_floor.generate_floor_type()
    intro_response, narrative = dm.non_combat_floor.generate_floor_intro()

    # Save the GameEvent
    GameEvent.objects.create(
        session=session,
        role=Role.NARRATOR,
        content=narrative,
        suggested_actions=intro_response.suggested_actions,
    )

    # Now update everything
    session.game_state = GameState.IN_PROGRESS
    session.save_dm(dm)

    # Return response
    return JsonResponse(
        {
            "narrative": narrative,
            "suggested_actions": intro_response.suggested_actions,
            "state": session.game_state,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def player_input(request: HttpRequest, session_id: int):
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)

    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    if session.game_state != GameState.IN_PROGRESS:
        return JsonResponse({"error": "Cannot interact in this state"}, status=400)

    try:
        data = json.loads(request.body)
        action = data["action"]
        suggested_actions = data["suggested_actions"]

    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Load the DM
    dm = session.load_dm()

    # Get the output from dm
    output = dm.non_combat_floor.handle_user_input(
        action, suggested_actions, verbose=False
    )

    # Check the output type
    if isinstance(output, HandleUserInputError):
        return JsonResponse({"error": output.error_message}, status=400)

    session.game_state = GameState.IN_PROGRESS

    # Save the GameEvents
    game_events = []
    for message in output.messages:
        game_event = GameEvent(
            session=session,
            role=Role(message["role"]),
            content=message["content"],
        )

        game_events.append(game_event)

    if isinstance(output, HandleUserInputSuggestedAction):
        game_events[-1].suggested_actions = output.suggested_actions

    # Bulk create all game events
    GameEvent.objects.bulk_create(game_events)

    # Save the dm
    session.save_dm(dm)

    # For different output type
    if isinstance(output, HandleUserInputEnd):
        session.game_state = GameState.WAITING_FOR_NEXT_FLOOR
        session.save()
        return JsonResponse(
            {
                "state": session.game_state,
                "events": output.messages,
            }
        )

    elif isinstance(output, HandleUserInputDefeat):
        session.game_state = GameState.COMPLETED
        session.save()
        return JsonResponse(
            {
                "state": session.game_state,
                "events": output.messages,
            }
        )

    else:
        return JsonResponse(
            {
                "state": session.game_state,
                "events": output.messages,
                "suggested_actions": output.suggested_actions,
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_session_info(request: HttpRequest, session_id: int):
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)

    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    # Get the player info or return 404 if not found
    try:
        player_info = session.player

    except PlayerInfo.DoesNotExist:
        return JsonResponse({"error": "Player info not found"}, status=404)

    # Create a dictionary with the player info
    player_data = {
        "player_name": player_info.player_name,
        "description": player_info.description,
        "current_health": player_info.current_health,
        "max_health": player_info.max_health,
        "strength": player_info.strength,
        "dexterity": player_info.dexterity,
        "constitution": player_info.constitution,
        "intelligence": player_info.intelligence,
        "wisdom": player_info.wisdom,
        "charisma": player_info.charisma,
    }

    # Create a dictionary with session info
    session_data = {
        "theme": session.theme,
        "current_floor": session.current_floor,
    }

    return JsonResponse({"player_info": player_data, "session_info": session_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_sessions(request: HttpRequest):
    # First, clean up invalid sessions
    user_sessions = GameSession.objects.filter(user=request.user)

    # Find and delete invalid sessions
    invalid_sessions = []
    for session in user_sessions:
        is_invalid = False

        # Check if session is missing required related models
        try:
            if not hasattr(session, "player"):
                is_invalid = True
            elif not hasattr(session, "non_combat_floor_model"):
                is_invalid = True
            elif not hasattr(session.non_combat_floor_model, "floor_history_model"):
                is_invalid = True

            if is_invalid:
                invalid_sessions.append(session.id)

        except Exception:
            # If any error occurs while checking, mark as invalid
            invalid_sessions.append(session.id)

    # Delete all invalid sessions in a single query
    if invalid_sessions:
        GameSession.objects.filter(id__in=invalid_sessions).delete()

    # Now get all valid sessions with related data
    sessions = GameSession.objects.filter(user=request.user).select_related(
        "player", "non_combat_floor_model__floor_history_model"
    )

    data = [
        {
            "id": session.id,
            "player_name": (
                session.player.player_name
                if hasattr(session, "player") and session.player
                else None
            ),
            "theme": session.theme,
            "current_floor": session.current_floor,
            "game_state": session.game_state,
        }
        for session in sessions
    ]

    return JsonResponse({"sessions": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_events(request: HttpRequest, session_id: int):
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)
    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    events = GameEvent.objects.filter(session=session).order_by("created_at")
    data = []
    for event in events:
        event_data = {
            "role": event.role,
            "content": event.content,
        }
        if event.suggested_actions:  # Only include if not empty
            event_data["suggested_actions"] = event.suggested_actions

        data.append(event_data)

    return JsonResponse({"events": data, "state": session.game_state})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_game_state(request: HttpRequest, session_id: int):
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)
    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    return JsonResponse({"state": session.game_state})
