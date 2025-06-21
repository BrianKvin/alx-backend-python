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
        
        # Both messages should be deleted (sent and received by user1)
        self.assertEqual(remaining_messages, 0)
        self.assertEqual(remaining_notifications, 0)


class CacheTest(TestCase):
    """Test cases for view caching."""
    
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
    
    def test_cache_configuration(self):
        """Test that cache is properly configured."""
        from django.conf import settings
        
        # Check cache settings
        self.assertIn('default', settings.CACHES)
        self.assertEqual(
            settings.CACHES['default']['BACKEND'], 
            'django.core.cache.backends.locmem.LocMemCache'
        )
        self.assertEqual(
            settings.CACHES['default']['LOCATION'], 
            'unique-snowflake'
        )
    
    def test_cache_functionality(self):
        """Test basic cache functionality."""
        # Test cache set and get
        cache.set('test_key', 'test_value', 30)
        cached_value = cache.get('test_key')
        self.assertEqual(cached_value, 'test_value')
        
        # Test cache expiry
        cache.set('expire_key', 'expire_value', 1)
        import time
        time.sleep(2)
        expired_value = cache.get('expire_key')
        self.assertIsNone(expired_value)


class AdvancedORMTest(TestCase):
    """Test cases for advanced ORM techniques."""
    
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
        
        # Create a conversation with replies
        self.parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        self.reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="First reply",
            parent_message=self.parent_message
        )
        
        self.reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Second reply",
            parent_message=self.parent_message
        )
    
    def test_select_related_optimization(self):
        """Test select_related for reducing database queries."""
        with self.assertNumQueries(1):
            # Should fetch message with related sender and receiver in one query
            message = Message.objects.select_related('sender', 'receiver').first()
            # Accessing related fields shouldn't trigger additional queries
            sender_name = message.sender.username
            receiver_name = message.receiver.username
    
    def test_prefetch_related_optimization(self):
        """Test prefetch_related for optimizing reverse foreign key queries."""
        with self.assertNumQueries(2):
            # Should fetch parent message and all replies in 2 queries
            parent = Message.objects.prefetch_related('replies').get(
                id=self.parent_message.id
            )
            # Accessing replies shouldn't trigger additional queries
            replies_count = parent.replies.count()
            self.assertEqual(replies_count, 2)
    
    def test_only_optimization(self):
        """Test .only() for fetching specific fields."""
        # Create a message with read=False
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for only() optimization"
        )
        
        # Use only() to fetch specific fields
        messages = Message.unread_objects.unread_for_user(self.user2).only(
            'content', 'timestamp'
        )
        
        # Should be able to access only specified fields efficiently
        for message in messages:
            content = message.content
            timestamp = message.timestamp
            # Accessing other fields would trigger additional queries
    
    def test_recursive_replies(self):
        """Test recursive reply functionality."""
        # Create nested replies
        nested_reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Nested reply",
            parent_message=self.reply1
        )
        
        # Test get_all_replies method
        all_replies = self.parent_message.get_all_replies()
        self.assertIn(self.reply1, all_replies)
        self.assertIn(self.reply2, all_replies)
        self.assertIn(nested_reply, all_replies)


class NotificationTest(TestCase):
    """Test cases for notification functionality."""
    
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
    
    def test_notification_creation(self):
        """Test notification model creation."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        notification = Notification.objects.create(
            user=self.user2,
            message=message,
            notification_type='message'
        )
        
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertFalse(notification.is_read)
    
    def test_notification_string_representation(self):
        """Test notification __str__ method."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        notification = Notification.objects.create(
            user=self.user2,
            message=message,
            notification_type='message'
        )
        
        expected_str = f"Notification for {self.user2.username}: New Message"
        self.assertEqual(str(notification), expected_str)


class MessageHistoryTest(TestCase):
    """Test cases for message history functionality."""
    
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
    
    def test_message_history_creation(self):
        """Test message history creation."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        history = MessageHistory.objects.create(
            message=message,
            old_content="Previous content"
        )
        
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, "Previous content")
    
    def test_multiple_edits_history(self):
        """Test multiple edits create multiple history records."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # First edit
        message.content = "First edit"
        message.save()
        
        # Second edit
        message.content = "Second edit"
        message.save()
        
        # Should have 2 history records
        history_count = MessageHistory.objects.filter(message=message).count()
        self.assertEqual(history_count, 2)
        
        # Check the order (most recent first)
        history_records = MessageHistory.objects.filter(message=message).order_by('-edited_at')
        self.assertEqual(history_records[0].old_content, "First edit")
        self.assertEqual(history_records[1].old_content, "Original content")