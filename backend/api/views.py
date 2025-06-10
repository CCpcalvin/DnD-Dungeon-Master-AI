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


# TODO: Handle non-authenticated user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_session(request: HttpRequest):
    # Create the session first
    session = GameSession.objects.create(
        user=request.user,
        theme="Dungeon Adventure",
        game_state=GameState.PLAYER_CREATION,
    )

    # Once the user start game, we will first init the DM
    dm = DungeonMaster(provider=ollama())

    # Generate theme, player backstory and player motivation
    background_response = dm.generate_theme()

    # Combine all the strings
    # We will send this strings as JSON to the frontend
    combined_content = (
        f"{background_response.theme} "
        f"{background_response.player_backstory} "
        f"{background_response.player_motivation} "
    )

    # Save to GameEvent for storage
    GameEvent.objects.create(
        session=session, role=Role.NARRATOR, content=combined_content
    )

    # Now we condense the story
    condensed_response = dm.condense_theme(
        theme=background_response.theme,
        player_backstory=background_response.player_backstory,
    )

    # Save the condensed theme to the session
    session.theme = condensed_response.theme

    # Create a player
    PlayerInfo.objects.create(
        session=session,
        description=condensed_response.player_backstory,
    )

    # Return information about the game
    return JsonResponse({"session_id": session.pk, "narrative": combined_content})


# TODO: Handle non-authenticated user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_player(request: HttpRequest, session_id: int):
    """
    Create a player for the session.

    This view should be called after the AI generates the theme and player backstory.
    """
    try:
        session: GameSession = GameSession.objects.get(pk=session_id)

    except GameSession.DoesNotExist:
        return JsonResponse({"error": "Session does not exist"}, status=404)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    if session.game_state != GameState.PLAYER_CREATION:
        return JsonResponse({"error": "Cannot create player in this state"}, status=400)

    try:
        data = json.loads(request.body)
        player_name = data["player_name"]
        strength = data["strength"]
        dexterity = data["dexterity"]
        constitution = data["constitution"]
        intelligence = data["intelligence"]
        wisdom = data["wisdom"]
        charisma = data["charisma"]

    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Server-validation
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

    # Get the player from the session
    player = session.player

    # Update the state
    player.player_name = player_name
    player.strength = strength
    player.dexterity = dexterity
    player.constitution = constitution
    player.intelligence = intelligence
    player.wisdom = wisdom
    player.charisma = charisma
    player.save()

    # Now we create necessary object for the game
    floor_history_model = FloorHistoryModel.objects.create(session=session, content=[])
    NonCombatFloorModel.objects.create(
        session=session, floor_history_model=floor_history_model
    )

    # Set the game state to in progress
    session.game_state = GameState.WAITING_FOR_NEXT_FLOOR
    session.save()

    # Return response
    return HttpResponse(status=200)


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
    GameEvent.objects.create(session=session, role=Role.NARRATOR, content=narrative)

    # Now update everything
    session.game_state = GameState.IN_PROGRESS
    session.save_dm(dm)

    # Return response
    return JsonResponse(
        {"narrative": narrative, "suggested_actions": intro_response.suggested_actions}
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
    for message in output.messages:
        GameEvent.objects.create(
            session=session,
            role=Role(message["role"]),
            content=message["content"],
        )

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
def get_player_info(request: HttpRequest, session_id: int):
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

    return JsonResponse({"player_info": player_data})
