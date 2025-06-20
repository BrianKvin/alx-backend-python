# messaging_app/chats/middleware.py

import logging
from datetime import datetime

# Get an instance of a logger
# It's good practice to define a logger for your middleware
# You'll configure where this logs to (file, console) in settings.py
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Middleware to log each user's request, including timestamp, user, and request path.
    """
    def __init__(self, get_response):
        """
        Initializes the middleware.
        'get_response' is a callable that takes a request and returns a response.
        Django passes this in during the server startup.
        """
        self.get_response = get_response
        # You could perform one-time configuration or setup here.
        # For logging, it's typically just storing get_response.

    def __call__(self, request):
        """
        Processes each request before the view is called and logs information.
        """
        # Get the current timestamp
        timestamp = datetime.now()

        # Get the user. If the user is authenticated, it will be a User object.
        # Otherwise, it might be an AnonymousUser object.
        # We'll display their username if available, or 'Anonymous' if not.
        user = request.user
        username = user.username if user.is_authenticated else 'Anonymous'

        # Get the request path
        path = request.path

        # Log the information
        log_message = f"{timestamp} - User: {username} - Path: {path}"
        logger.info(log_message) # Use logger.info to write the log

        # Call the next middleware or the view
        response = self.get_response(request)

        # You could also add post-response logging here if needed

        return response