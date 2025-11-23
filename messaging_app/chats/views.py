from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageSenderOrReadOnly
from .filters import MessageFilter
from .pagination import MessagePagination

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    Only participants can view and interact with conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    lookup_field = 'conversation_id'

    def get_queryset(self):
        """
        Filter conversations to only show those where the user is a participant
        """
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new conversation with the current user as a participant
        """
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a participant to the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            from .models import User
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': 'Participant added successfully'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    Only participants of the conversation can view/send messages
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation, IsMessageSenderOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    lookup_field = 'message_id'

    def get_queryset(self):
        """
        Filter messages to only show those in conversations where user is a participant
        Uses Message.objects.filter to restrict access
        """
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')

    def perform_create(self, serializer):
        """
        Create a new message with the current user as the sender
        Check if user is participant before allowing message creation
        """
        conversation = serializer.validated_data.get('conversation')
        
        # Verify user is a participant of the conversation
        if self.request.user not in conversation.participants.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a participant of this conversation to send messages.")
        
        serializer.save(sender=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Update a message - only sender can update
        """
        instance = self.get_object()
        
        # Check if user is the sender
        if instance.sender != request.user:
            return Response(
                {'error': 'You can only update your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a message - only sender can delete
        """
        instance = self.get_object()
        
        # Check if user is the sender
        if instance.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
