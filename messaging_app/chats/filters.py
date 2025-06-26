import django_filters
from django.db.models import Q # For combining queries
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model() 

class MessageFilter(django_filters.FilterSet):
    """
    Filter for messages with specific users or within a time range.
    """
    # Filter messages within a time range using 'sent_at' field
    # You can use __gte for 'greater than or equal to' and __lte for 'less than or equal to'
    # Example usage: ?sent_at_after=2023-01-01T00:00:00&sent_at_before=2023-01-31T23:59:59
    sent_at_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_at_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    # Filter messages exchanged with a specific user (either as sender or receiver)
    # This assumes your Message model has a 'sender' (ForeignKey to User)
    # and that the 'Conversation' model has 'participants' (ManyToManyField to User).
    # We'll filter based on the participants in the message's conversation.
    # Example usage: ?with_user=username_of_other_user
    with_user = django_filters.CharFilter(method='filter_with_user', label='Filter by username of other participant')

    class Meta:
        model = Message
        fields = {
            'sent_at': ['date__gte', 'date__lte', 'year', 'month', 'day'], 
        }

    def filter_with_user(self, queryset, name, value):
        """
        Custom filter method to retrieve messages exchanged with a specific user.
        This filters messages where the requesting user is in the conversation,
        AND the specified 'value' (username) corresponds to another participant in that conversation.
        """
        try:
            target_user = User.objects.get(username=value)
        except User.DoesNotExist:
            return queryset.none()

        # The core logic: find conversations where BOTH the requesting user AND the target_user are participants.
        # Then, filter messages belonging to those conversations.
        # Assuming request.user is available in the filterset context (passed from view)
        requesting_user = self.request.user

        if requesting_user.is_authenticated:
            conversations_with_both = requesting_user.conversations.filter(participants=target_user)

            # Filter messages that belong to these conversations
            return queryset.filter(conversation__in=conversations_with_both).distinct()
        return queryset.none() 

class ConversationFilter(django_filters.FilterSet):
    participant = django_filters.NumberFilter(field_name='participants__user_id')

    class Meta:
        model = Conversation
        fields = ['participant']