from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UnreadMessagesManager(models.Manager):
  """Custom manager to filter unread messages for a user."""
  def unread_for_user(self, user):
    """Get all unread messages for a specific user."""
    return self.filter(recipient=user, read=False)
  
  def unread_count_for_user(self, user):
    """Get the count of unread messages for a specific user."""
    return self.unread_for_user(user).count()
  
class Message(models.Model):
  """Model representing a message in the messaging system."""
  sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
  receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
  content = models.TextField()
  timestamp = models.DateTimeField(default=timezone.now)
  read = models.BooleanField(default=False)
  edited = models.BooleanField(default=False)
  parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
  objects = models.Manager()  # Default manager
  unread_messages = UnreadMessagesManager()  # Custom manager for unread messages
  class Meta:
    ordering = ['-timestamp']  

  def __str__(self):
    return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"

  def get_all_replies(self):
    """Get all replies to this message recursively."""
    replies = []
    for reply in self.reply.all():
      replies.append(reply)
      replies.extend(reply.get_all_replies())
    return replies
  
  def is_thread_starter(self):
    """Check if this message is the start of a thread."""
    return self.parent_message is None
  
class MessageHistory(models.Model):
  """Model to track message history."""  
  message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
  old_content = models.TextField()
  edited_at = models.DateTimeField(auto_now=True)
  edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edited_messages')

  class Meta:
    ordering = ['-edited_at'] 
    verbose_name_plural = "Message Histories"

  def __str__(self):
    return f"History for message {self.message.id} edited at {self.edited_at}"
  
class Notification(models.Model):
  """Model to store user notifications."""

  NOTIFICATION_TYPES = [
    ('message', 'New Message'),
    ('reply', 'Message Reply'),
    ('edit', 'Message Edited'), 
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
  message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
  notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='message')
  is_read = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at']
    verbose_name_plural = "Notifications"

  def __str__(self):
    return f"Notification for {self.user.username} - {self.notification_type} on message {self.message.id} at {self.created_at}"
