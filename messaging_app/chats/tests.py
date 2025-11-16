#!/usr/bin/env python3
"""Tests for chats application."""
from django.test import TestCase
from .models import User, Conversation, Message


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'guest')


class ConversationModelTest(TestCase):
    """Test cases for Conversation model."""
    
    def test_conversation_creation(self):
        """Test creating a conversation."""
        conversation = Conversation.objects.create()
        self.assertIsNotNone(conversation.conversation_id)


class MessageModelTest(TestCase):
    """Test cases for Message model."""
    
    def test_message_creation(self):
        """Test creating a message."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        conversation = Conversation.objects.create()
        message = Message.objects.create(
            sender=user,
            conversation=conversation,
            message_body='Test message'
        )
        self.assertEqual(message.message_body, 'Test message')
        self.assertEqual(message.sender, user)
```

6. Click **"Commit new file"**

---

## 📂 **File Location:**
```
messaging_app/
└── chats/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── tests.py        ← CREATE THIS HERE
