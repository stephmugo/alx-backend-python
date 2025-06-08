from rest_framework import permissions
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class that ensures:
    1. Only authenticated users can access the API
    2. Only participants in a conversation can send, view, update and delete messages
    3. Users can only access conversations they are part of
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before allowing any access
        """
        # First check: User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation related to the object
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            # Handle different object types
            conversation = None
            
            # If the object is a message, get its conversation
            if hasattr(obj, 'conversation'):
                conversation = obj.conversation
            
            # If the object is a conversation itself
            elif hasattr(obj, 'participants'):
                conversation = obj
            
            # If we found a conversation, check if user is a participant
            if conversation:
                # Check if user is in the participants
                if hasattr(conversation, 'participants'):
                    is_participant = conversation.participants.filter(id=request.user.id).exists()
                    
                    if request.method in permissions.SAFE_METHODS:
                        # For read operations (GET, HEAD, OPTIONS), allow if user is participant
                        return is_participant
                    else:
                        # For write operations (POST, PUT, PATCH, DELETE)
                        if hasattr(obj, 'sender'):
                            # For messages, user must be participant AND sender to modify
                            if request.method in ['PUT', 'PATCH', 'DELETE']:
                                return is_participant and obj.sender == request.user
                            # For creating messages, user must be participant
                            else:
                                return is_participant
                        else:
                            # For conversation modifications, user must be participant
                            return is_participant
                
                # Handle direct message pattern (sender/recipient)
                elif hasattr(conversation, 'sender') and hasattr(conversation, 'recipient'):
                    user_in_dm = request.user in [conversation.sender, conversation.recipient]
                    
                    if request.method in permissions.SAFE_METHODS:
                        return user_in_dm
                    else:
                        if hasattr(obj, 'sender'):
                            # For messages in DM, check if user is sender for modifications
                            if request.method in ['PUT', 'PATCH', 'DELETE']:
                                return user_in_dm and obj.sender == request.user
                            else:
                                return user_in_dm
                        else:
                            return user_in_dm
            
            # If no conversation found or accessible, deny access
            return False
            
        except (ObjectDoesNotExist, AttributeError) as e:
            # If there's any error accessing the conversation, deny access
            return False