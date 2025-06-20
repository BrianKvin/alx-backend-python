from rest_framework.permissions import BasePermission

class IsOwnerOrParticipant(BasePermission):
    """
    Custom permission to only allow owners or participants to access objects.
    """
    def has_object_permission(self, request, view, obj):
        # Example: check if user is a participant in a conversation
        return request.user in obj.participants.all()