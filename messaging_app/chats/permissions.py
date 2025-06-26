from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users who are participants
    of a conversation to access/modify its related messages and the conversation itself.
    """

    message = "You do not have permission to access this conversation or messages."

    def has_permission(self, request, view):
        """
        Check if the user is authenticated for any API access.
        This covers the "Allow only authenticated users to access the API" requirement.
        """
        # User must be authenticated to access any part of the API protected by this permission
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation object.
        This covers "Allow only participants in a conversation to send, view, update and delete messages".
        Note: 'obj' could be a Conversation instance or a Message instance.
        """
        # Read permissions are allowed to any authenticated user who is a participant.
        # Write permissions (POST, PUT, PATCH, DELETE) are also restricted to participants.

        # If obj is a Conversation instance
        if hasattr(obj, 'participants'):
            # For conversation objects, check if the user is one of the participants
            return request.user in obj.participants.all()

        # If obj is a Message instance, it must belong to a conversation
        # and the user must be a participant of that conversation.
        # Assuming Message model has a 'conversation' ForeignKey.
        if hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return request.user in obj.conversation.participants.all()

        # Fallback for other objects if necessary, or deny by default
        return False

class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Custom permission to allow only the sender of a message or a participant
    in the conversation to access/modify the message.
    """
    message = "You must be the sender or a participant in the conversation."

    def has_object_permission(self, request, view, obj):
        # obj should be a Message instance
        return (
            hasattr(obj, 'sender') and request.user == obj.sender or
            hasattr(obj, 'conversation') and request.user in obj.conversation.participants.all()
        )