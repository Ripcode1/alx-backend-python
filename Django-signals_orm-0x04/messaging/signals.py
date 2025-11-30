from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to automatically create a notification when a new message is created.
    Triggered after a Message is saved.
    """
    if created:
        # Determine notification type based on whether it's a reply
        notification_type = 'reply' if instance.parent_message else 'message'
        
        # Create notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type=notification_type,
            content=f"You have a new {'reply' if instance.parent_message else 'message'} from {instance.sender.username}"
        )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal to log message edits before saving.
    Captures the old content and stores it in MessageHistory.
    """
    if instance.pk:  # Only for existing messages (updates, not creates)
        try:
            # Get the old version of the message
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if old_message.content != instance.content:
                # Mark message as edited
                instance.edited = True
                
                # Create history record
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is the editor
                )
                
                # Create notification for the receiver about the edit
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    notification_type='edit',
                    content=f"{instance.sender.username} edited their message"
                )
        except Message.DoesNotExist:
            # Message doesn't exist yet, skip logging
            pass


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Signal to clean up all user-related data when a user is deleted.
    Deletes messages, notifications, and message histories.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Delete all message edit history by the user
    MessageHistory.objects.filter(edited_by=instance).delete()
    
    # Note: Cascade deletion will handle related data automatically
    # if CASCADE is set on foreign keys, but this ensures explicit cleanup
