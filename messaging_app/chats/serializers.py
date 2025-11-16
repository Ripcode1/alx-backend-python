#!/usr/bin/env python3
"""Serializers for the chats application."""
from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at',
            'full_name'
        ]
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with nested sender information."""
    
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'sender_name',
            'conversation',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def get_sender_name(self, obj):
        """Get the sender's full name."""
        return obj.sender.get_full_name() if obj.sender else None
    
    def validate_message_body(self, value):
        """Validate that message body is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value
    
    def create(self, validated_data):
        """Create a new message."""
        sender_id = validated_data.pop('sender_id')
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")
        
        message = Message.objects.create(sender=sender, **validated_data)
        return message


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested participants and messages."""
    
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'participant_count',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        """Get the number of participants in the conversation."""
        return obj.participants.count()
    
    def validate_participant_ids(self, value):
        """Validate that participant_ids list is not empty."""
        if not value:
            raise serializers.ValidationError("At least one participant is required.")
        return value
    
    def create(self, validated_data):
        """Create a new conversation with participants."""
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create()
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            if participants.count() != len(participant_ids):
                raise serializers.ValidationError("One or more participant IDs are invalid.")
            conversation.participants.set(participants)
        
        return conversation
