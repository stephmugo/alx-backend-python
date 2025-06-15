from django.db import models
from django.contrib.auth import get_user_model


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for handling unread message queries.
    
    Provides efficient methods for retrieving unread messages
    with proper validation and optimizations.
    """
    
    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        
        Args:
            user: User instance or user ID
            
        Returns:
            QuerySet: Filtered queryset of unread messages for the user
            
        Raises:
            ValueError: If user is None or invalid
        """
        if user is None:
            raise ValueError("User cannot be None")
        
        # Handle both User instances and user IDs
        user_id = user.pk if hasattr(user, 'pk') else user
        
        return self.filter(
            receiver_id=user_id,  # Use receiver_id for efficiency (avoids JOIN)
            is_read=False
        ).select_related('sender')  # Optimize for common access patterns
    
    def mark_as_read_for_user(self, user):
        """
        Mark all unread messages as read for a specific user.
        
        Args:
            user: User instance or user ID
            
        Returns:
            int: Number of messages marked as read
        """
        if user is None:
            raise ValueError("User cannot be None")
            
        user_id = user.pk if hasattr(user, 'pk') else user
        
        return self.filter(
            receiver_id=user_id,
            is_read=False
        ).update(is_read=True)
    
    def unread_count_for_user(self, user):
        """
        Get count of unread messages for a user (more efficient than len()).
        
        Args:
            user: User instance or user ID
            
        Returns:
            int: Count of unread messages
        """
        if user is None:
            return 0
            
        user_id = user.pk if hasattr(user, 'pk') else user
        
        return self.filter(
            receiver_id=user_id,
            is_read=False
        ).count()