from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def index(request):
    """
    Render the index page.
    """
    return HttpResponse("dnd game master is running.")


def session_new(request):
    """
    Handle the creation of a new session.
    """
    # Logic for creating a new session would go here
    return JsonResponse({"session_id": 1})
