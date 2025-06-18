import django_filters
from .models import Conversation, Message

class ConversationFilter(django_filters.FilterSet):
    class Meta:
        model = Conversation
        fields = ['participants'] 

class MessageFilter(django_filters.FilterSet):
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'is_read']