from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # User
    path("user/register", views.CreateUserView.as_view(), name="register"),
    path("user/token", TokenObtainPairView.as_view(), name="get_token"),
    path("user/token/refresh", TokenRefreshView.as_view(), name="refresh_token"),
    # Game
    path("session/create-game", views.create_game, name="create_game"),
    path(
        "session/<int:session_id>/new-floor",
        views.new_floor,
        name="new_floor",
    ),
    path(
        "session/<int:session_id>/player-input",
        views.player_input,
        name="player_input",
    ),
    path(
        "session/<int:session_id>/get-session-info",
        views.get_session_info,
        name="get_session_info",
    ),
    path("get-sessions", views.get_sessions, name="get_sessions"),
    path("session/<int:session_id>/get-events", views.get_events, name="get_events"),
    path(
        "session/<int:session_id>/get-game-state",
        views.get_game_state,
        name="get_game_state",
    ),
]
