from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    filterset_fields = ['role']

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation operations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        # Filter conversations to only show those the user participates in
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(participants=self.request.user)
        return Conversation.objects.none()
    
    def perform_create(self, serializer):
        # Automatically add the current user as a participant
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a participant to an existing conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'message': 'Participant added successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    filterset_fields = ['conversation', 'sender']
    
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
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        Send a message to an existing conversation
        """
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')
        
        if not conversation_id or not message_body:
            return Response(
                {'error': 'conversation_id and message_body are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {'error': 'You are not a participant in this conversation'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            message = Message.objects.create(
                sender=request.user,
                conversation=conversation,
                message_body=message_body
            )
            
            serializer = self.get_serializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )