from rest_framework import serializers
from .models import User, Conversation, Message
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField()

    def validate_email(self, value):
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'date_joined']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'recipient', 'message_body', 'sent_at', 'conversation']
        read_only_fields = ('sender', 'sent_at', 'recipient', 'conversation')

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    messages = MessageSerializer(many=True, read_only=True)
    last_message_preview = serializers.SerializerMethodField()

    def get_last_message_preview(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.message_body[:50] + '...'
        return None

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'name', 'participants', 'messages', 'created_at', 'last_message_preview']
        read_only_fields = ['conversation_id', 'messages', 'created_at']