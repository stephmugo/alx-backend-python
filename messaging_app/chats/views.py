from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Conversation, Message
from .permissions import IsParticipantOfConversation

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations with participant-based permissions
    """
    # serializer_class = ConversationSerializer  # You'll create this
    permission_classes = [IsParticipantOfConversation]
    
    # Add filtering backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['participants', 'created_at']
    search_fields = ['participants__username', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']  # Default ordering
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant
        """
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        
        # Filter conversations where user is a participant
        return Conversation.objects.filter(
            participants=self.request.user
        ).distinct().order_by('-updated_at')
    
    def perform_create(self, serializer):
        """
        Create a new conversation and add the creator as a participant
        """
        conversation = serializer.save(created_by=self.request.user)
        # Add creator as participant
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsParticipantOfConversation])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation
        Only existing participants can add new participants
        """
        conversation = self.get_object()
        username = request.data.get('username')
        
        if not username:
            return Response({
                'error': 'Username is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_add = User.objects.get(username=username)
            
            if user_to_add in conversation.participants.all():
                return Response({
                    'error': 'User is already a participant'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            conversation.participants.add(user_to_add)
            
            return Response({
                'message': f'User {username} added to conversation',
                'participants': [p.username for p in conversation.participants.all()]
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[IsParticipantOfConversation])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation
        Only existing participants can remove participants
        Users can remove themselves
        """
        conversation = self.get_object()
        username = request.data.get('username')
        
        if not username:
            return Response({
                'error': 'Username is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_remove = User.objects.get(username=username)
            
            if user_to_remove not in conversation.participants.all():
                return Response({
                    'error': 'User is not a participant'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Users can only remove themselves or if they're the creator
            if user_to_remove != request.user and conversation.created_by != request.user:
                return Response({
                    'error': 'You can only remove yourself or you must be the conversation creator'
                }, status=status.HTTP_403_FORBIDDEN)
            
            conversation.participants.remove(user_to_remove)
            
            return Response({
                'message': f'User {username} removed from conversation',
                'participants': [p.username for p in conversation.participants.all()]
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[IsParticipantOfConversation])
    def messages(self, request, pk=None):
        """
        Get all messages in a conversation
        Only participants can view messages
        """
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('created_at')
        
        # You'll create MessageSerializer
        # serializer = MessageSerializer(messages, many=True)
        # return Response(serializer.data)
        
        # Placeholder response
        return Response({
            'conversation_id': conversation.id,
            'message_count': messages.count(),
            'messages': 'Message serialization will be implemented with MessageSerializer'
        })


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages with participant-based permissions
    """
    # serializer_class = MessageSerializer  # You'll create this
    permission_classes = [IsParticipantOfConversation]
    
    # Add filtering backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'is_read', 'created_at']
    search_fields = ['content', 'sender__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Return messages from conversations where the current user is a participant
        """
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        
        # Filter messages from conversations where user is a participant
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).distinct().order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Create a new message with the current user as sender
        """
        serializer.save(sender=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update message - only sender can update their own messages
        """
        message = self.get_object()
        
        if message.sender != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own messages")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete message - only sender can delete their own messages
        """
        if instance.sender != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own messages")
        
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[IsParticipantOfConversation])
    def mark_as_read(self, request, pk=None):
        """
        Mark a message as read by the current user
        """
        message = self.get_object()
        
        # Add logic to mark message as read
        # This might involve a MessageReadStatus model
        
        return Response({
            'message': 'Message marked as read',
            'message_id': message.id
        }, status=status.HTTP_200_OK)