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
        current_floor=1,
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
        return JsonResponse({"error": "Session does not exist"}, status=400)

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
    session.game_state = GameState.IN_PROGRESS

    # Load the DM
    dm = session.load_dm()

    # Now we start the floor
    floor = dm.non_combat_floor
    floor.generate_floor_type()
    intro_response, narrative = floor.generate_floor_intro()

    # Save the GameEvent
    GameEvent.objects.create(session=session, role=Role.NARRATOR, content=narrative)

    # Now update everything
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
        return JsonResponse({"error": "Session does not exist"}, status=402)

    if session.user != request.user:
        return JsonResponse({"error": "You do not own this session"}, status=403)

    if session.game_state != GameState.IN_PROGRESS:
        return JsonResponse({"error": "Cannot interact in this state"}, status=400)

    try:
        data = json.loads(request.body)
        action = data["action"]

    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Load the DM
    dm = session.load_dm()

    # Get the output from dm
    output = dm.non_combat_floor.handle_user_input(action, verbose=False)

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
                "events": output.messages,
            }
        )

    elif isinstance(output, HandleUserInputDefeat):
        session.game_state = GameState.DEFEATED
        session.save()
        return JsonResponse(
            {
                "events": output.messages,
            }
        )

    else:
        return JsonResponse(
            {
                "events": output.messages,
                "suggested_actions": output.suggested_actions,
            }
        )
