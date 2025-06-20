# messaging_app/chats/middleware.py

import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from django.conf import settings
from collections import defaultdict

# Get an instance of a logger for general request logging
request_logger = logging.getLogger(__name__)

# Dictionary to store IP addresses and their request timestamps for rate limiting
# In a production environment, this would ideally be a persistent store like Redis or a database cache.
# For this exercise, an in-memory dictionary is sufficient.
IP_REQUEST_TIMESTAMPS = defaultdict(list)
RATE_LIMIT_MESSAGES = 5
RATE_LIMIT_WINDOW_SECONDS = 60 # 1 minute

class RequestLoggingMiddleware:
    """
    Middleware to log each user's request, including timestamp, user, and request path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timestamp = datetime.now()
        user = request.user
        username = user.username if user.is_authenticated else 'Anonymous'
        path = request.path
        log_message = f"{timestamp} - User: {username} - Path: {path}"
        request_logger.info(log_message)

        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging app during certain hours of the day.
    Denies access outside 6 AM (06:00) and 9 PM (21:00).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_start_hour = 6  # 6 AM
        self.allowed_end_hour = 21   # 9 PM (21:00)

    def __call__(self, request):
        current_time = datetime.now().time()

        # Check if the current time is outside the allowed window
        # Not allowed if it's before 6 AM OR after or exactly 9 PM
        if not (self.allowed_start_hour <= current_time.hour < self.allowed_end_hour):
            return HttpResponseForbidden("Access to the messaging app is restricted during these hours (6 AM - 9 PM).")

        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware: # Renamed as per instructions, but implements rate limiting
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.
    Limits to 5 messages per minute for POST requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply rate limiting to POST requests which are typically message sending
        # You might adjust this to specific API paths if needed (e.g., /api/messages/)
        if request.method == 'POST':
            # Get the client's IP address
            # Be aware: In production, you might need to handle 'X-Forwarded-For' headers
            # if your app is behind a proxy/load balancer.
            ip_address = request.META.get('REMOTE_ADDR')

            if ip_address:
                current_time = datetime.now()

                # Clean up old timestamps (older than RATE_LIMIT_WINDOW_SECONDS)
                # Keep only timestamps within the last minute
                IP_REQUEST_TIMESTAMPS[ip_address] = [
                    ts for ts in IP_REQUEST_TIMESTAMPS[ip_address]
                    if current_time - ts < timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)
                ]

                # Add the current request's timestamp
                IP_REQUEST_TIMESTAMPS[ip_address].append(current_time)

                # Check if the number of requests exceeds the limit
                if len(IP_REQUEST_TIMESTAMPS[ip_address]) > RATE_LIMIT_MESSAGES:
                    return HttpResponseForbidden(
                        f"You have exceeded the message sending limit of {RATE_LIMIT_MESSAGES} messages per {RATE_LIMIT_WINDOW_SECONDS / 60} minute."
                    )

        response = self.get_response(request)
        return response

class RolePermissionMiddleware:
    """
    Middleware that checks the user’s role (admin/moderator) before allowing access
    to specific actions/paths.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that only admins/moderators can access
        # This is an example; adjust these paths to fit your actual admin/moderator actions
        self.admin_restricted_paths = [
            '/admin/',          # Django admin site
            '/api/users/',      # Example: A user management API endpoint
            # Add other paths that require admin/moderator roles
        ]

    def __call__(self, request):
        # Access to Django admin is handled by Django itself, but we can enforce
        # additional checks for other 'admin-like' API endpoints.
        # Check if the requested path is in the restricted list
        for restricted_path in self.admin_restricted_paths:
            if request.path.startswith(restricted_path):
                # If the path is restricted, check user's authentication and role
                if not request.user.is_authenticated:
                    return HttpResponseForbidden("Access Denied: Authentication required.")

                # Check if the user is a superuser or staff (moderator)
                # You might have a custom 'is_moderator' field or group check here.
                if not (request.user.is_superuser or request.user.is_staff):
                    return HttpResponseForbidden("Access Denied: Insufficient role permissions (Admin/Moderator required).")
                # If they are admin/staff, let the request continue to the view
                break # Exit the loop, permission granted for this path

        response = self.get_response(request)
        return response