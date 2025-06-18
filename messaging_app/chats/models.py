# messaging_app/chats/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
import uuid


class User(AbstractUser):
    """
    Extended User model for additional fields not in Django's built-in User model
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password: models.CharField(max_length=128, help_text="User's password") 
    role = models.CharField(
        max_length=10,
        choices=[
            ('guest', 'Guest'),
            ('host', 'Host'),
            ('admin', 'Admin')
        ],
        default='guest'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override username to use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model to track conversations between users
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        help_text="Users participating in this conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ", ".join([str(user) for user in self.participants.all()[:2]])
        participant_count = self.participants.count()
        if participant_count > 2:
            return f"Conversation: {participant_names} and {participant_count - 2} others"
        return f"Conversation: {participant_names}"

    @property
    def last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-sent_at').first()


class Message(models.Model):
    """
    Model for individual messages within conversations
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent this message"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversation this message belongs to"
    )
    message_body = models.TextField(help_text="Content of the message")
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for message status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender', 'sent_at']),
        ]

    def __str__(self):
        preview = self.message_body[:50] + "..." if len(self.message_body) > 50 else self.message_body
        return f"{self.sender.first_name}: {preview}"

    def save(self, *args, **kwargs):
        """Override save to update conversation's updated_at timestamp"""
        super().save(*args, **kwargs)
        # Update the conversation's updated_at field when a new message is added
        self.conversation.save(update_fields=['updated_at'])

    def mark_as_read(self):
        """Mark this message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = models.functions.Now()
            self.save(update_fields=['is_read', 'read_at'])


# Additional model for tracking message read status per user (optional)
class MessageReadStatus(models.Model):
    """
    Track read status of messages per user in group conversations
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_status'
        unique_together = ['message', 'user']
        
    def __str__(self):
        return f"{self.user.first_name} read message {self.message.message_id}"