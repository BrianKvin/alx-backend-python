from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a new message is created.
    """
    if created:
        # Determine notification type based on whether it's a reply
        notification_type = 'reply' if instance.parent_message else 'message'
        
        # Create notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type=notification_type
        )
        
        # If it's a reply, also notify the original sender
        if instance.parent_message and instance.parent_message.sender != instance.receiver:
            Notification.objects.create(
                user=instance.parent_message.sender,
                message=instance,
                notification_type='reply'
            )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal to log message edits before saving the updated message.
    """
    if instance.pk:  # Only for existing messages (updates)
        try:
            # Get the original message from database
            original_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if original_message.content != instance.content:
                # Create history record with old content
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content
                )
                
                # Mark message as edited
                instance.edited = True
                
        except Message.DoesNotExist:
            # Message doesn't exist yet, so it's a new message
            pass


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal to clean up user-related data when a user is deleted.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Note: MessageHistory records will be automatically deleted due to CASCADE
    # relationship when their associated messages are deleted