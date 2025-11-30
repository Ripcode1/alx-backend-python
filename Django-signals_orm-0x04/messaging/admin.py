from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    list_display = ['id', 'sender', 'receiver', 'content_preview', 'timestamp', 'edited', 'read', 'parent_message']
    list_filter = ['edited', 'read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']
    date_hierarchy = 'timestamp'
    raw_id_fields = ['sender', 'receiver', 'parent_message']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('sender', 'receiver', 'content', 'parent_message')
        }),
        ('Status', {
            'fields': ('edited', 'read', 'timestamp')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    list_display = ['id', 'user', 'notification_type', 'content_preview', 'timestamp', 'read']
    list_filter = ['notification_type', 'read', 'timestamp']
    search_fields = ['user__username', 'content']
    date_hierarchy = 'timestamp'
    raw_id_fields = ['user', 'message']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        """Show preview of notification content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model"""
    list_display = ['id', 'message', 'old_content_preview', 'edited_at', 'edited_by']
    list_filter = ['edited_at']
    search_fields = ['message__content', 'old_content', 'edited_by__username']
    date_hierarchy = 'edited_at'
    raw_id_fields = ['message', 'edited_by']
    readonly_fields = ['edited_at']
    
    def old_content_preview(self, obj):
        """Show preview of old content"""
        return obj.old_content[:50] + '...' if len(obj.old_content) > 50 else obj.content
    old_content_preview.short_description = 'Old Content Preview'
