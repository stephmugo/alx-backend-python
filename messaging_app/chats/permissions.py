from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission for conversations:
    - Only participants can access the conversation
    - Only participants can add messages to the conversation
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'participants'):  # This is a conversation
            return request.user in obj.participants.all()
        
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsMessageOwnerOrConversationParticipant(permissions.BasePermission):
    """
    Custom permission for messages:
    - Message owner can read/edit their own messages
    - Conversation participants can read messages in their conversations
    - Only message owner can edit/delete their messages
    """
    
    def has_object_permission(self, request, view, obj):
        # For messages, check if user is the sender or a participant in the conversation
        if hasattr(obj, 'sender'):  # This is a message
            # User can read if they're the sender or participant in conversation
            if request.method in permissions.SAFE_METHODS:
                return (obj.sender == request.user or 
                       request.user in obj.conversation.participants.all())
            
            # User can only edit/delete their own messages
            return obj.sender == request.user
        
        return False