from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user"""
    def unread_for_user(self, user):
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp', 'read'
        )


class Message(models.Model):
    """Model for storing messages between users with threading support"""
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    objects = models.Manager()
    unread_objects = UnreadMessagesManager()
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['parent_message']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
    
    def get_thread(self):
        """Recursively get all replies to this message"""
        return Message.objects.filter(
            parent_message=self
        ).prefetch_related(
            'sender',
            'receiver',
            'replies'
        ).select_related('sender', 'receiver')


class Notification(models.Model):
    """Model for storing user notifications"""
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('reply', 'Message Reply'),
        ('edit', 'Message Edited'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='message'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_type}"


class MessageHistory(models.Model):
    """Model for storing message edit history"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_edits'
    )
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message histories'
    
    def __str__(self):
        return f"Edit of message {self.message.id} at {self.edited_at}"
