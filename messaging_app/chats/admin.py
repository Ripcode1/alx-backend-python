#!/usr/bin/env python3
"""Admin configuration for chats application."""
from django.contrib import admin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""
    list_display = ['email', 'username', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""
    list_display = ['conversation_id', 'created_at', 'participant_count']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = ['message_id', 'sender', 'conversation', 'sent_at']
    list_filter = ['sent_at']
    search_fields = ['message_body', 'sender__email']
    ordering = ['-sent_at']
