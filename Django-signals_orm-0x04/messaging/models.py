import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from .managers import UnreadMessagesManager

# Use get_user_model() for better flexibility with custom user models
User = get_user_model()


class Message(models.Model):
    """
    Model representing messages between users.
    
    Supports threaded conversations through parent_message relationship
    and tracks read status and edit history.
    """
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Preserve messages if user is deleted
        related_name='received_messages', 
        null=True,
        blank=True,
        help_text="User who receives the message"
    )
    content = models.TextField(
        help_text="Message content",
        max_length=5000  # Reasonable limit to prevent abuse
    )
    edited = models.BooleanField(
        default=False,
        help_text="Whether this message has been edited"
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,  # Index for faster unread queries
        help_text="Whether the receiver has read this message"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Index for faster ordering/filtering
        help_text="When the message was created"
    )
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,  # Fixed: was missing models.
        null=True, 
        blank=True, 
        related_name='replies',
        help_text="Parent message if this is a reply"
    )
    
    # Managers
    objects = models.Manager()  # Fixed: was missing parentheses
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['-timestamp']  # Return newest messages first
        indexes = [
            # Composite indexes for common query patterns
            models.Index(fields=['receiver', 'is_read']),
            models.Index(fields=['sender', 'timestamp']),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
    def __str__(self):
        """String representation of the message."""
        receiver_name = self.receiver.username if self.receiver else "Unknown"
        # Fixed: removed invalid colon in f-string
        return f'Message from {self.sender.username} to {receiver_name} at {self.timestamp}'
    
    def clean(self):
        """Validate the model data."""
        super().clean()
        
        # Prevent self-messaging
        if self.sender == self.receiver:
            raise ValidationError("Cannot send message to yourself")
        
        # Validate parent message belongs to same conversation
        if self.parent_message:
            if (self.parent_message.sender != self.receiver or 
                self.parent_message.receiver != self.sender):
                raise ValidationError("Reply must be in same conversation thread")
    
    def mark_as_read(self):
        """Mark this message as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    def can_be_edited_by(self, user):
        """Check if a user can edit this message."""
        return self.sender == user and not self.edited
    
    @property
    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.parent_message is not None


class MessageHistory(models.Model):
    """
    Model to track edit history of messages.
    
    Maintains an audit trail of all message modifications.
    """
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='history',
        help_text="The message that was edited"
    )
    content = models.TextField(
        help_text="Previous content before edit"
    )
    edited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the edit occurred"
    )
    edited_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Preserve history even if user deleted
        null=True,
        related_name='message_edits',  # More descriptive related name
        help_text="User who made the edit"
    )
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"
    
    def __str__(self):
        editor = self.edited_by.username if self.edited_by else "Unknown"
        return f"Edit by {editor} at {self.edited_at}"


class Notification(models.Model):
    """
    Model for user notifications.
    
    Supports different notification types and links to related messages.
    """
    
    # Notification type choices
    class NotificationType(models.TextChoices):
        MESSAGE = 'message', 'New Message'
        FRIEND_REQUEST = 'friend_request', 'Friend Request'
        SYSTEM = 'system', 'System Alert'
        REPLY = 'reply', 'Message Reply'  # Added reply type
    
    notification_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the notification"
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="User receiving the notification"
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sent_notifications',
        help_text="User who triggered the notification"
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Related message if applicable"
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,  # Index for faster unread queries
        help_text="Whether the recipient has read this notification"
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NotificationType.choices,
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=255,
        help_text="Notification title/subject"
    )
    body = models.TextField(
        blank=True,
        help_text="Detailed notification content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Index for faster ordering
        help_text="When the notification was created"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Composite index for common queries
            models.Index(fields=['recipient', 'is_read']),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"Notification for {self.recipient.username} ({self.get_notification_type_display()})"
    
    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    @classmethod
    def create_message_notification(cls, message):
        """
        Create a notification for a new message.
        
        Args:
            message: Message instance that triggered the notification
            
        Returns:
            Notification: Created notification instance
        """
        if not message.receiver:
            return None
            
        return cls.objects.create(
            recipient=message.receiver,
            sender=message.sender,
            message=message,
            notification_type=cls.NotificationType.REPLY if message.is_reply else cls.NotificationType.MESSAGE,
            title=f"New {'reply' if message.is_reply else 'message'} from {message.sender.username}",
            body=message.content[:100] + "..." if len(message.content) > 100 else message.content
        )