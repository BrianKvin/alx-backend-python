from django.contrib import admin
from .models import Message, MessageHistory, Notification


class MessageHistoryInline(admin.TabularInline):
    """Inline admin for message edit history."""
    model = MessageHistory
    extra = 0
    readonly_fields = ('old_content', 'edited_at')
    can_delete = False


class NotificationInline(admin.TabularInline):
    """Inline admin for message notifications."""
    model = Notification
    extra = 0
    readonly_fields = ('notification_type', 'is_read', 'created_at')
    can_delete = False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    
    list_display = (
        'id', 
        'sender', 
        'receiver', 
        'content_preview', 
        'timestamp', 
        'edited', 
        'read', 
        'parent_message'
    )
    list_filter = ('edited', 'read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
    raw_id_fields = ('sender', 'receiver', 'parent_message')
    readonly_fields = ('timestamp',)
    inlines = [MessageHistoryInline, NotificationInline]
    
    def content_preview(self, obj):
        """Show a preview of the message content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('sender', 'receiver', 'parent_message')


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for MessageHistory model."""
    
    list_display = ('id', 'message', 'old_content_preview', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'old_content')
    raw_id_fields = ('message',)
    readonly_fields = ('edited_at',)
    
    def old_content_preview(self, obj):
        """Show a preview of the old content."""
        return obj.old_content[:50] + "..." if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = "Old Content Preview"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = (
        'id', 
        'user', 
        'message', 
        'notification_type', 
        'is_read', 
        'created_at'
    )
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    raw_id_fields = ('user', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'message')