from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# Customizing the Token Payload (adding user-specific data to JWT)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT token payload to include user information.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # Assuming you have a 'user_id' field on your custom User model
        if hasattr(user, 'user_id'):
            token['user_id'] = str(user.user_id) # Convert UUID to string if applicable
        # Add other user fields as needed, e.g., first_name, last_name, roles, etc.

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens with extended user data.
    This view will be used in your urls.py.
    """
    serializer_class = CustomTokenObtainPairSerializer