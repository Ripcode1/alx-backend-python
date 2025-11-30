from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, log_message_edit, delete_user_related_data


class MessageModelTest(TestCase):
    """Test cases for Message model"""
    
    def setUp(self):
        """Set up test users"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
    
    def test_message_creation(self):
        """Test basic message creation"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, World!'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Hello, World!')
        self.assertFalse(message.edited)
        self.assertFalse(message.read)
    
    def test_message_threading(self):
        """Test parent-child message relationship"""
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Parent message'
        )
        
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Reply message',
            parent_message=parent_message
        )
        
        self.assertEqual(reply.parent_message, parent_message)
        self.assertIn(reply, parent_message.replies.all())
    
    def test_unread_messages_manager(self):
        """Test custom UnreadMessagesManager"""
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message',
            read=False
        )
        
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Read message',
            read=True
        )
        
        unread_messages = Message.unread_objects.unread_for_user(self.user2)
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first().content, 'Unread message')


class MessageSignalTest(TestCase):
    """Test cases for message signals"""
    
    def setUp(self):
        """Set up test users"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
    
    def test_notification_created_on_new_message(self):
        """Test that notification is created when a new message is sent"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test notification'
        )
        
        notifications = Notification.objects.filter(user=self.user2, message=message)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().notification_type, 'message')
    
    def test_notification_for_reply(self):
        """Test that reply notification is created for threaded messages"""
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Parent message'
        )
        
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Reply',
            parent_message=parent_message
        )
        
        notification = Notification.objects.filter(user=self.user1, message=reply).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, 'reply')
    
    def test_message_edit_logging(self):
        """Test that message edits are logged in MessageHistory"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original content'
        )
        
        # Edit the message
        message.content = 'Edited content'
        message.save()
        
        # Check that message is marked as edited
        message.refresh_from_db()
        self.assertTrue(message.edited)
        
        # Check that history was created
        history = MessageHistory.objects.filter(message=message)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().old_content, 'Original content')
    
    def test_no_history_on_first_save(self):
        """Test that no history is created on initial message creation"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='New message'
        )
        
        history_count = MessageHistory.objects.filter(message=message).count()
        self.assertEqual(history_count, 0)


class UserDeletionSignalTest(TransactionTestCase):
    """Test cases for user deletion signal"""
    
    def setUp(self):
        """Set up test users and data"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create messages
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message 1'
        )
        
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Message 2'
        )
    
    def test_user_deletion_cleanup(self):
        """Test that all user-related data is deleted when user is deleted"""
        user1_id = self.user1.id
        
        # Delete user1
        self.user1.delete()
        
        # Check that messages sent by user1 are deleted
        sent_messages = Message.objects.filter(sender__id=user1_id)
        self.assertEqual(sent_messages.count(), 0)
        
        # Check that messages received by user1 are deleted
        received_messages = Message.objects.filter(receiver__id=user1_id)
        self.assertEqual(received_messages.count(), 0)
        
        # Check that notifications for user1 are deleted
        notifications = Notification.objects.filter(user__id=user1_id)
        self.assertEqual(notifications.count(), 0)


class MessageQueryOptimizationTest(TestCase):
    """Test cases for ORM query optimization"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create parent message
        self.parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Parent'
        )
        
        # Create replies
        for i in range(3):
            Message.objects.create(
                sender=self.user2,
                receiver=self.user1,
                content=f'Reply {i}',
                parent_message=self.parent
            )
    
    def test_get_thread_optimization(self):
        """Test that get_thread uses prefetch_related efficiently"""
        with self.assertNumQueries(2):  # Should use prefetch to minimize queries
            thread = self.parent.get_thread()
            # Access related objects
            for message in thread:
                _ = message.sender.username
                _ = message.receiver.username
    
    def test_select_related_optimization(self):
        """Test select_related for foreign key optimization"""
        with self.assertNumQueries(1):
            messages = Message.objects.select_related('sender', 'receiver').filter(
                receiver=self.user2
            )
            for message in messages:
                _ = message.sender.username
                _ = message.receiver.username


class NotificationModelTest(TestCase):
    """Test cases for Notification model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='pass123')
    
    def test_notification_creation(self):
        """Test notification creation"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='message',
            content='Test notification'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.notification_type, 'message')
        self.assertFalse(notification.read)
