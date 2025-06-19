import logging
from functools import wraps

import openai
from django.http import JsonResponse

from .models import GameSession

logger = logging.getLogger(__name__)


def handle_llm_errors(view_func):
    """
    A decorator to handle common LLM-related errors and return appropriate JSON responses.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except openai.APIConnectionError as e:
            logger.error(f"LLM API Connection Error: {str(e)}")
            return JsonResponse(
                {
                    "error": "Failed to connect to the AI service. Please check your internet connection and try again."
                },
                status=503,
            )

        except openai.APIError as e:
            logger.error(f"LLM API Error: {str(e)}")
            return JsonResponse(
                {
                    "error": "An error occurred while processing your request with the AI service. Please try again later."
                },
                status=500,
            )

    return _wrapped_view


def validate_session(view_func):
    """
    A decorator to validate session existence and ownership.
    Adds the session instance to the view's kwargs.
    """

    @wraps(view_func)
    def _wrapped_view(request, session_id, *args, **kwargs):
        try:
            session = GameSession.objects.get(pk=session_id)
            if session.user != request.user:
                return JsonResponse(
                    {"error": "You do not own this session"}, status=403
                )

            # Add session to kwargs for the view function
            kwargs["session"] = session
            return view_func(request, session_id, *args, **kwargs)

        except GameSession.DoesNotExist:
            return JsonResponse({"error": "Session does not exist"}, status=404)

    return _wrapped_view


def handle_unknown_error(view_func):
    """
    A decorator to handle unknown errors and return appropriate JSON responses.
    This will not handle APIConnectionError, which should be handled by handle_llm_errors.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"Unknown error: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    "error": "An unknown error occurred. Please try again later.",
                },
                status=500,
            )

    return _wrapped_view

