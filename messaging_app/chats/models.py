#!/usr/bin/env python3
"""Models for the chats application."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended User model with additional fields.
    
    Attributes:
        user_id: UUID primary key
        first_name: User's first name
        last_name: User's last name
        email: Unique email address
        password_hash: Hashed password (inherited)
        phone_number: Optional phone number
        role: User role (guest, host, admin)
        created_at: Timestamp when user was created
    """
    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    email = models.EmailField(unique=True)
    
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for User model."""
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
        ]
        
    def __str__(self):
        """String representation."""
        return f"{self.email} ({self.role})"


class Conversation(models.Model):
    """Model representing a conversation between users.
    
    Attributes:
        conversation_id: UUID primary key
        participants: Many-to-many relationship with User
        created_at: Timestamp when conversation was created
    """
    
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for Conversation model."""
        db_table = 'conversations'
        ordering = ['-created_at']
        
    def __str__(self):
        """String representation."""
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """Model representing a message in a conversation.
    
    Attributes:
        message_id: UUID primary key
        sender: Foreign key to User who sent the message
        conversation: Foreign key to Conversation
        message_body: Text content of the message
        sent_at: Timestamp when message was sent
    """
    
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_body = models.TextField()
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for Message model."""
        db_table = 'messages'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender']),
        ]
        
    def __str__(self):
        """String representation."""
        return f"Message {self.message_id} from {self.sender.email}"
