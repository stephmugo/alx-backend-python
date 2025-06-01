from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation operations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'
    
    def get_queryset(self):
        # Filter conversations to only show those the user participates in
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(participants=self.request.user)
        return Conversation.objects.none()
    
    def perform_create(self, serializer):
        # Automatically add the current user as a participant
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    
    def get_queryset(self):
        # Filter messages to only show those in conversations the user participates in
        if self.request.user.is_authenticated:
            user_conversations = Conversation.objects.filter(participants=self.request.user)
            return Message.objects.filter(conversation__in=user_conversations)
        return Message.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set the sender to the current user
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='conversation/(?P<conversation_id>[^/.]+)')
    def by_conversation(self, request, conversation_id=None):
        """
        Get all messages for a specific conversation
        """
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        # Check if user is a participant in the conversation
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = Message.objects.filter(conversation=conversation)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)