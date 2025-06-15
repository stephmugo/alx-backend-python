import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import Message, Notification, MessageHistory

# Get user model for flexibility
User = get_user_model()

# Set up logging for signal debugging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Create notification when a new message is sent.
    
    Only creates notifications for new messages (not updates) and
    only if the receiver exists and is different from sender.
    
    Args:
        sender: Message model class
        instance: Message instance that was saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional signal arguments
    """
    if not created or not instance.receiver:
        return
    
    # Don't create notification for self-messages (extra safety)
    if instance.sender == instance.receiver:
        return
    
    try:
        # Use the model's class method for consistent notification creation
        notification = Notification.create_message_notification(instance)
        if notification:
            logger.info(f"Created notification {notification.notification_id} for message {instance.id}")
    except Exception as e:
        logger.error(f"Failed to create notification for message {instance.id}: {str(e)}")


@receiver(pre_save, sender=Message)
def track_message_edits(sender, instance, **kwargs):
    """
    Track message edits by creating history records.
    
    Compares current content with stored content and creates
    a history record if changes are detected.
    
    Args:
        sender: Message model class
        instance: Message instance being saved
        **kwargs: Additional signal arguments
    """
    # Only process existing messages (not new ones)
    if not instance.pk:
        return
    
    try:
        # Get the current version from database
        try:
            old_message = Message.objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            logger.warning(f"Message {instance.pk} not found in database during pre_save")
            return
        
        # Check if content has actually changed
        if old_message.content == instance.content:
            return
        
        # Create history record with atomic transaction
        with transaction.atomic():
            MessageHistory.objects.create(
                message=instance,
                content=old_message.content,
                edited_by=instance.sender  # Assumes sender is making the edit
            )
            
            # Mark message as edited
            instance.edited = True
            
        logger.info(f"Created edit history for message {instance.pk}")
        
    except Exception as e:
        logger.error(f"Failed to create edit history for message {instance.pk}: {str(e)}")


@receiver(post_save, sender=Message)
def update_notification_on_read(sender, instance, created, **kwargs):
    """
    Handle notification updates when messages are marked as read.
    
    This could be used to update related notification status
    or perform other actions when a message is read.
    
    Args:
        sender: Message model class
        instance: Message instance that was saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional signal arguments
    """
    # Only process existing messages that are now read
    if created or not instance.is_read:
        return
    
    try:
        # Update related notifications to read status
        related_notifications = Notification.objects.filter(
            message=instance,
            recipient=instance.receiver,
            is_read=False
        )
        
        if related_notifications.exists():
            count = related_notifications.update(is_read=True)
            logger.info(f"Marked {count} notifications as read for message {instance.id}")
            
    except Exception as e:
        logger.error(f"Failed to update notifications for message {instance.id}: {str(e)}")


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up user-related data when a user is deleted.
    
    Handles cleanup of messages, notifications, and history records
    associated with the deleted user. Uses database transactions
    for data consistency.
    
    Args:
        sender: User model class
        instance: User instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        with transaction.atomic():
            # Count records before deletion for logging
            message_count = Message.objects.filter(
                Q(sender=instance) | Q(receiver=instance)
            ).count()
            
            history_count = MessageHistory.objects.filter(
                edited_by=instance
            ).count()
            
            notification_count = Notification.objects.filter(
                Q(recipient=instance) | Q(sender=instance)
            ).count()
            
            # Perform cleanup operations
            # Note: Messages with receiver=instance will have receiver set to NULL
            # due to SET_NULL on the foreign key, preserving the message content
            Message.objects.filter(sender=instance).delete()
            
            # Clean up message history
            MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)
            
            # Clean up notifications
            Notification.objects.filter(
                Q(recipient=instance) | Q(sender=instance)
            ).delete()
            
            logger.info(
                f"Cleaned up user {instance.username} data: "
                f"{message_count} messages, {history_count} history records, "
                f"{notification_count} notifications"
            )
            
    except Exception as e:
        logger.error(f"Failed to cleanup data for user {instance.username}: {str(e)}")
        # Re-raise to prevent user deletion if cleanup fails
        raise


@receiver(post_delete, sender=Message)
def cleanup_message_references(sender, instance, **kwargs):
    """
    Clean up references when a message is deleted.
    
    Removes related notifications and history records
    to maintain database consistency.
    
    Args:
        sender: Message model class
        instance: Message instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        with transaction.atomic():
            # Clean up related notifications
            notification_count = Notification.objects.filter(message=instance).count()
            Notification.objects.filter(message=instance).delete()
            
            # History records are automatically deleted due to CASCADE relationship
            # but we log for monitoring
            history_count = MessageHistory.objects.filter(message=instance).count()
            
            logger.info(
                f"Cleaned up message {instance.id} references: "
                f"{notification_count} notifications, {history_count} history records"
            )
            
    except Exception as e:
        logger.error(f"Failed to cleanup references for message {instance.id}: {str(e)}")


# Signal connection verification
def verify_signal_connections():
    """
    Utility function to verify signal connections are working.
    
    Can be called during app initialization or testing to ensure
    all signals are properly connected.
    """
    try:
        from django.db.models.signals import post_save, pre_save, post_delete
        
        # Check if our receivers are connected
        post_save_receivers = [r for r in post_save._live_receivers(sender=Message)]
        pre_save_receivers = [r for r in pre_save._live_receivers(sender=Message)]
        post_delete_receivers = [r for r in post_delete._live_receivers(sender=User)]
        
        logger.info(f"Signal connections verified: "
                   f"post_save: {len(post_save_receivers)}, "
                   f"pre_save: {len(pre_save_receivers)}, "
                   f"post_delete: {len(post_delete_receivers)}")
        
        return True
    except Exception as e:
        logger.error(f"Signal verification failed: {str(e)}")
        return False