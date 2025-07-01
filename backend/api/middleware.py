from django.utils import timezone

from .constants import USER_LAST_MODIFIED_UPDATE_INTERVAL

class UpdateLastModifiedMiddleware:
    """
    Middleware to update the last_modified field for the authenticated user on each request.
    Updates the timestamp at most once per minute to reduce database load.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request and get the response
        response = self.get_response(request)
        
        # Check if the user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'last_modified'):
            # Only update if last_modified is older than the defined interval to reduce database writes
            update_threshold = timezone.now() - USER_LAST_MODIFIED_UPDATE_INTERVAL
            if request.user.last_modified is None or request.user.last_modified < update_threshold:
                # Update the last_modified field
                request.user.last_modified = timezone.now()
                # Save only the last_modified field to be more efficient
                request.user.save(update_fields=['last_modified'])
        
        return response
