from rest_framework import permissions

class IsParticipantInConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # obj here is a Conversation instance
        return request.user in obj.participants.all()

class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow the message sender or a conversation participant to access a message.
    """
    def has_object_permission(self, request, view, obj):
        # obj here is a Message instance
        # Allow sender to see/manage their message
        if obj.sender == request.user:
            return True
        # Allow any participant in the conversation to see the message
        return request.user in obj.conversation.participants.all()

