from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation 
    to view, send, update, and delete messages within that conversation.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before accessing the API
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation.
        Allow PUT, PATCH, DELETE only for participants.
        """
        # For Message objects, check if user is participant of the conversation
        if hasattr(obj, 'conversation'):
            is_participant = request.user in obj.conversation.participants.all()
            
            # For PUT, PATCH, DELETE - only participants allowed
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant
            
            return is_participant
        
        # For Conversation objects, check if user is a participant
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
            
            # For PUT, PATCH, DELETE - only participants allowed
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant
                
            return is_participant
        
        return False

class IsMessageSenderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant (handled by IsParticipantOfConversation)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions (PUT, PATCH, DELETE) are only allowed to the message sender
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        return obj.sender == request.user
