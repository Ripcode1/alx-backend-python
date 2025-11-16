#!/usr/bin/env python3
"""Views for the chats application."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model.
    
    Provides full CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
    ordering = ['-created_at']


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model.
    
    Provides endpoints to:
    - List all conversations
    - Create a new conversation
    - Retrieve a specific conversation
    - Update a conversation
    - Delete a conversation
    - Add participants to conversations
    """
    queryset = Conversation.objects.all().prefetch_related(
        'participants',
        'messages__sender'
    )
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """Add a participant to an existing conversation."""
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
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """Remove a participant from a conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model.
    
    Provides endpoints to:
    - List all messages
    - Create a new message (send message to existing conversation)
    - Retrieve a specific message
    - Update a message
    - Delete a message
    
    Supports filtering by conversation_id and sender.
    """
    queryset = Message.objects.all().select_related(
        'sender',
        'conversation'
    ).order_by('-sent_at')
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__email', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Filter messages by conversation or sender if specified in query params."""
        queryset = super().get_queryset()
        
        # Filter by conversation_id
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(
                conversation__conversation_id=conversation_id
            )
        
        # Filter by sender_id
        sender_id = self.request.query_params.get('sender_id')
        if sender_id:
            queryset = queryset.filter(sender__user_id=sender_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Send a message to an existing conversation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
