from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message, MessageHistory, Notification

# Use get_user_model() for better flexibility
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with safe field exposure.
    
    Only exposes non-sensitive user information for public APIs.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        """Get user's full name or fallback to username."""
        if hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            full_name = f"{obj.first_name} {obj.last_name}".strip()
            return full_name if full_name else obj.username
        return obj.username


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested relationships.
    
    Used to avoid circular references and reduce payload size.
    """
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class MessageSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Message model.
    
    Handles nested user data, reply counts, and proper validation.
    """
    sender = SimpleUserSerializer(read_only=True)
    receiver = SimpleUserSerializer(read_only=True)
    reply_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    # Write-only fields for creating messages
    receiver_id = serializers.IntegerField(write_only=True, required=False)
    parent_message_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'content', 'edited', 'is_read',
            'timestamp', 'parent_message', 'reply_count', 'can_edit',
            'time_since_created', 'receiver_id', 'parent_message_id'
        ]
        read_only_fields = [
            'id', 'sender', 'receiver', 'edited', 'timestamp', 'parent_message'
        ]
        extra_kwargs = {
            'content': {
                'max_length': 5000,
                'min_length': 1,
                'error_messages': {
                    'blank': 'Message content cannot be empty.',
                    'max_length': 'Message content cannot exceed 5000 characters.'
                }
            }
        }
    
    def get_reply_count(self, obj):
        """Get the number of replies to this message."""
        return obj.replies.count()
    
    def get_can_edit(self, obj):
        """Check if current user can edit this message."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_be_edited_by(request.user)
        return False
    
    def get_time_since_created(self, obj):
        """Get human-readable time since message creation."""
        now = timezone.now()
        diff = now - obj.timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def validate(self, attrs):
        """Validate message data."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        # Set sender to current user
        attrs['sender'] = request.user
        
        # Validate receiver
        receiver_id = attrs.get('receiver_id')
        if receiver_id:
            try:
                receiver = User.objects.get(id=receiver_id)
                if receiver == request.user:
                    raise serializers.ValidationError("Cannot send message to yourself")
                attrs['receiver'] = receiver
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid receiver specified")
        
        # Validate parent message
        parent_message_id = attrs.get('parent_message_id')
        if parent_message_id:
            try:
                parent_message = Message.objects.get(id=parent_message_id)
                # Ensure reply is in same conversation
                if (parent_message.sender != request.user and 
                    parent_message.receiver != request.user):
                    raise serializers.ValidationError("Can only reply to messages in your conversations")
                attrs['parent_message'] = parent_message
            except Message.DoesNotExist:
                raise serializers.ValidationError("Invalid parent message specified")
        
        return attrs
    
    def create(self, validated_data):
        """Create a new message with proper cleanup."""
        # Remove write-only fields before creating
        validated_data.pop('receiver_id', None)
        validated_data.pop('parent_message_id', None)
        return super().create(validated_data)


class MessageHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for message edit history.
    
    Provides audit trail for message modifications.
    """
    edited_by = SimpleUserSerializer(read_only=True)
    message_id = serializers.IntegerField(source='message.id', read_only=True)
    
    class Meta:
        model = MessageHistory
        fields = ['id', 'message_id', 'content', 'edited_by', 'edited_at']
        read_only_fields = ['id', 'message_id', 'edited_by', 'edited_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for notifications.
    
    Includes related object data and user-friendly formatting.
    """
    sender = SimpleUserSerializer(read_only=True)
    recipient = SimpleUserSerializer(read_only=True)
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', 
        read_only=True
    )
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'notification_id', 'recipient', 'sender', 'message', 'is_read',
            'notification_type', 'notification_type_display', 'title', 'body',
            'created_at', 'time_since_created'
        ]
        read_only_fields = [
            'notification_id', 'recipient', 'sender', 'created_at'
        ]
    
    def get_time_since_created(self, obj):
        """Get human-readable time since notification creation."""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class MessageUpdateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for updating messages.
    
    Handles edit history creation and validation.
    """
    class Meta:
        model = Message
        fields = ['content']
        extra_kwargs = {
            'content': {
                'max_length': 5000,
                'min_length': 1,
                'error_messages': {
                    'blank': 'Message content cannot be empty.',
                    'max_length': 'Message content cannot exceed 5000 characters.'
                }
            }
        }
    
    def update(self, instance, validated_data):
        """Update message and create history record."""
        request = self.context.get('request')
        
        # Validate user can edit
        if not request or not instance.can_be_edited_by(request.user):
            raise serializers.ValidationError("You cannot edit this message")
        
        # Store original content in history
        if instance.content != validated_data.get('content'):
            MessageHistory.objects.create(
                message=instance,
                content=instance.content,
                edited_by=request.user
            )
            
            # Mark as edited
            validated_data['edited'] = True
        
        return super().update(instance, validated_data)


class ConversationSerializer(serializers.Serializer):
    """
    Serializer for conversation threads.
    
    Groups messages between two users with pagination support.
    """
    other_user = SimpleUserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    last_message_at = serializers.DateTimeField(read_only=True)