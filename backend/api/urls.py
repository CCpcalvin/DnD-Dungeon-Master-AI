from django.urls import path

from .views import (
    index,
    CreateUserView,
    create_game,
    player_input,
    new_floor,
    get_player_info,
    get_sessions,
    get_events,
    get_game_state,
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", index, name="index"),
    # User
    path("user/register", CreateUserView.as_view(), name="register"),
    path("user/token", TokenObtainPairView.as_view(), name="get_token"),
    path("user/token/refresh", TokenRefreshView.as_view(), name="refrest_token"),
    # Game
    path("session/create-game", create_game, name="create_game"),
    path(
        "session/<int:session_id>/new-floor",
        new_floor,
        name="new_floor",
    ),
    path(
        "session/<int:session_id>/player-input",
        player_input,
        name="player_input",
    ),
    path(
        "session/<int:session_id>/player-info",
        get_player_info,
        name="get_player_info",
    ),
    path("get-sessions", get_sessions, name="get_sessions"),
    path("session/<int:session_id>/get-events", get_events, name="get_events"),
    path(
        "session/<int:session_id>/get-game-state", get_game_state, name="get_game_state"
    ),
]
