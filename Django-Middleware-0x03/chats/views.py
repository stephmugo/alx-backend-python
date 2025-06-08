from .pagination import MessagePagination
from .filters import MessageFilter
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .permissions import IsSender, IsParticipantOfConversation
from django_filters import rest_framework as filters

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender, IsParticipantOfConversation]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['participants', 'created_at']
    ordering_fields = ['sent_at']

    def create(self, request, *args, **kwargs):
        participants = request.data.get("participants", [])
        if not participants:
            return Response(
                {"detail": "Participants list cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_id_str = str(request.user.user_id)
        if user_id_str not in participants:
            return Response(
                {"detail": "You must be one of the participants to create this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).order_by('-created_at')

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]
    pagination_class = MessagePagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MessageFilter

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_pk"]
        return Message.objects.filter(conversation_id=conversation_id).order_by('-sent_at')

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = Conversation.objects.get(pk=conversation_id)
        serializer.save(sender=self.request.user, conversation=conversation)