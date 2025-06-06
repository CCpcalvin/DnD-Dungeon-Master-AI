from django.urls import path
from .views import index, session_new

urlpatterns = [
    path("", index, name="index"),
    path("session/new/", session_new, name="session_new"),
]
