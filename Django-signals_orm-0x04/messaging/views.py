from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Message, Notification, MessageHistory
from .serializers import (
    UserSerializer,
    MessageSerializer,
    NotificationSerializer,
    MessageHistorySerializer,
)
from .managers import UnreadMessagesManager


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['delete'], url_path='custom-delete')
    def delete_user(self, request, pk=None):
        """
        Custom user deletion endpoint.
        DELETE /users/{id}/custom-delete/
        """
        user = self.get_object()
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling user messages.
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        """
        Return messages sent by the current user.
        """
        return Message.objects.filter(sender=self.request.user)

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        """
        Cached list of messages (overrides list to enable caching).
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Return unread messages for the current user.
        """
        unread_messages = (
            Message.unread
            .unread_for_user(request.user)
            .only('sender_id', 'content', 'timestamp')
            .select_related('sender')
        )
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """
        Return all messages sent by the current user (could be renamed for clarity).
        """
        messages = (
            Message.objects
            .filter(sender=request.user)
            .select_related('sender', 'receiver')
            .prefetch_related('replies')
        )
        serializer = self.get_serializer(messages, many=True)
        return JsonResponse(serializer.data, safe=False)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notifications.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Return notifications for the current user.
        """
        return Notification.objects.filter(recipient=self.request.user)


class MessageHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for message history.
    """
    queryset = MessageHistory.objects.all()
    serializer_class = MessageHistorySerializer
