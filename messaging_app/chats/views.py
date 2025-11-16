#!/usr/bin/env python3
"""Views for the chats application."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model.
    
    Provides endpoints to:
    - List all conversations
    - Create a new conversation
    - Retrieve a specific conversation
    - Update a conversation
    - Delete a conversation
    """
    
    queryset = Conversation.objects.all().prefetch_related(
        'participants',
        'messages'
    )
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """Add a participant to a conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model.
    
    Provides endpoints to:
    - List all messages
    - Create a new message (send message to existing conversation)
    - Retrieve a specific message
    - Update a message
    - Delete a message
    """
    
    queryset = Message.objects.all().select_related(
        'sender',
        'conversation'
    )
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    
    def get_queryset(self):
        """Filter messages by conversation if specified."""
        queryset = super().get_queryset()
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            queryset = queryset.filter(
                conversation__conversation_id=conversation_id
            )
        
        return queryset
