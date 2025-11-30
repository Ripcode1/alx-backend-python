from django.db import models


class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user"""
    def unread_for_user(self, user):
        """
        Filter unread messages for a specific user.
        Uses only() to optimize field loading.
        
        Args:
            user: The user to filter messages for
            
        Returns:
            QuerySet of unread messages for the user
        """
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp', 'read'
        )
