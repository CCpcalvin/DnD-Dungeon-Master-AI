from django.urls import path

from .views import (
    index,
    CreateUserView,
    new_session,
    create_player,
    player_input,
    new_floor,
    get_player_info,
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", index, name="index"),
    # User
    path("user/register", CreateUserView.as_view(), name="register"),
    path("user/token", TokenObtainPairView.as_view(), name="get_token"),
    path("user/token/refresh", TokenRefreshView.as_view(), name="refrest_token"),
    # Game
    path("session/new", new_session, name="session_new"),
    path(
        "session/<int:session_id>/create-player",
        create_player,
        name="create_player",
    ),
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
]
