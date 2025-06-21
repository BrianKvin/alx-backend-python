from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete
from django.test.utils import override_settings
from django.core.cache import cache
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, log_message_edit, cleanup_user_data


class MessageModelTest(TestCase):
    """Test cases for Message model and its custom manager."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', 
            email='test1@example.com', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com', 
            password='testpass123'
        )
    
    def test_message_creation(self):
        """Test basic message creation."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.edited)
        self.assertFalse(message.read)
        self.assertIsNone(message.parent_message)
    
    def test_threaded_message(self):
        """Test threaded message functionality."""
        # Create parent message
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply to original message",
            parent_message=parent_message
        )
        
        self.assertEqual(reply.parent_message, parent_message)
        self.assertTrue(parent_message.is_thread_starter())
        self.assertFalse(reply.is_thread_starter())
        self.assertIn(reply, parent_message.replies.all())
    
    def test_unread_messages_manager(self):
        """Test custom UnreadMessagesManager."""
        # Create some messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 1"
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            read=True
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 2"
        )
        
        # Test unread messages for user2
        unread_messages = Message.unread_objects.unread_for_user(self.user2)
        self.assertEqual(unread_messages.count(), 2)
        
        # Test unread count
        unread_count = Message.unread_objects.unread_count_for_user(self.user2)
        self.assertEqual(unread_count, 2)


class SignalTest(TestCase):
    """Test cases for Django signals."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', 
            email='test1@example.com', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com', 
            password='testpass123'
        )
    
    def test_notification_signal(self):
        """Test that notifications are created when messages are sent."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for notification"
        )
        
        # Check that notification was created
        notifications = Notification.objects.filter(user=self.user2, message=message)
        self.assertEqual(notifications.count(), 1)
        
        notification = notifications.first()
        self.assertEqual(notification.notification_type, 'message')
        self.assertFalse(notification.is_read)
    
    def test_reply_notification_signal(self):
        """Test that reply notifications are created correctly."""
        # Create parent message
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent_message
        )
        
        # Check that reply notification was created for original sender
        reply_notifications = Notification.objects.filter(
            user=self.user1, 
            message=reply, 
            notification_type='reply'
        )
        self.assertEqual(reply_notifications.count(), 1)
    
    def test_message_edit_logging(self):
        """Test that message edits are logged in MessageHistory."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check that edit history was created
        history = MessageHistory.objects.filter(message=message)
        self.assertEqual(history.count(), 1)
        
        history_record = history.first()
        self.assertEqual(history_record.old_content, "Original content")
        
        # Check that message is marked as edited
        message.refresh_from_db()
        self.assertTrue(message.edited)
    
    def test_user_deletion_cleanup(self):
        """Test that user data is cleaned up when user is deleted."""
        # Create some data for the user
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message from user1"
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message to user1"
        )
        
        # Create notification
        notification = Notification.objects.create(
            user=self.user1,
            message=message1
        )
        
        # Count initial data
        initial_messages = Message.objects.count()
        initial_notifications = Notification.objects.count()
        
        # Delete user1
        self.user1.delete()
        
        # Check that related data was cleaned up
        remaining_messages = Message.objects.count()
        remaining_notifications = Notification.objects.count()
        
        # Both messages should be delete