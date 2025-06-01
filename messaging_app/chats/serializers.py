from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'created_at', 'full_name', 'display_name'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_display_name(self, obj):
        """
        SerializerMethodField to get display name
        """
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username
    
    def validate_email(self, value):
        """
        Custom validation for email field
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'sender_name', 
            'conversation', 'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """
        Validate message body is not empty
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids', 'messages', 
            'created_at', 'participant_count', 'last_message'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        """
        Get the number of participants in the conversation
        """
        return obj.participants.count()
    
    def get_last_message(self, obj):
        """
        Get the last message in the conversation
        """
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.get_full_name() or last_message.sender.username
            }
        return None
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            if not participants.exists():
                raise serializers.ValidationError("One or more participant IDs are invalid.")
            conversation.participants.set(participants)
        
        return conversation
    
    def validate_participant_ids(self, value):
        """
        Validate that all participant IDs exist
        """
        if value:
            existing_users = User.objects.filter(user_id__in=value)
            if len(existing_users) != len(value):
                raise serializers.ValidationError("One or more participant IDs do not exist.")
        return value