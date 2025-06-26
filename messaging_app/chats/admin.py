from django.contrib import admin
from .models import Message, Conversation

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'message_body', 'sent_at', 'conversation', 'is_read')
    list_filter = ('sent_at', 'sender', 'is_read')
    search_fields = ('message_body', 'sender__username')
    date_hierarchy = 'sent_at'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'created_at', 'updated_at', 'participant_count')
    list_filter = ('created_at',)
    filter_horizontal = ('participants',)
    date_hierarchy = 'created_at'

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'