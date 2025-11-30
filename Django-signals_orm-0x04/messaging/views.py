from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Q
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User


@login_required
def delete_user(request):
    """
    View to allow a user to delete their account.
    All related data will be automatically cleaned up via signals.
    """
    if request.method == 'POST':
        user = request.user
        # Log out the user before deletion
        from django.contrib.auth import logout
        logout(request)
        # Delete the user (signals will handle cleanup)
        user.delete()
        django_messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    
    return render(request, 'messaging/delete_user_confirm.html')


@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_list(request, conversation_id=None):
    """
    Display list of messages in a conversation with caching.
    Uses select_related and prefetch_related for optimization.
    """
    user = request.user
    
    # Get all messages for the user (sent and received)
    messages_query = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related(
        'sender', 
        'receiver', 
        'parent_message'
    ).prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
    ).order_by('-timestamp')
    
    if conversation_id:
        # Filter to specific conversation
        other_user = get_object_or_404(User, id=conversation_id)
        messages_query = messages_query.filter(
            Q(sender=user, receiver=other_user) | 
            Q(sender=other_user, receiver=user)
        )
    
    context = {
        'messages': messages_query,
        'user': user,
        'conversation_id': conversation_id
    }
    
    return render(request, 'messaging/conversation_list.html', context)


@login_required
def inbox(request):
    """
    Display user's inbox with unread messages using custom manager.
    Uses only() to optimize field loading.
    """
    user = request.user
    
    # Get unread messages using custom manager
    unread_messages = Message.unread.unread_for_user(user)
    
    # Get all received messages with optimization
    all_messages = Message.objects.filter(
        receiver=user
    ).select_related('sender').only(
        'id', 'sender', 'content', 'timestamp', 'read', 'edited'
    ).order_by('-timestamp')
    
    context = {
        'unread_messages': unread_messages,
        'all_messages': all_messages,
        'unread_count': unread_messages.count()
    }
    
    return render(request, 'messaging/inbox.html', context)


@login_required
def message_detail(request, message_id):
    """
    Display a single message with its full thread of replies.
    Uses recursive querying and optimization techniques.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message'),
        id=message_id
    )
    
    # Check if user is authorized to view this message
    if message.sender != request.user and message.receiver != request.user:
        return HttpResponseForbidden("You don't have permission to view this message.")
    
    # Mark as read if user is the receiver
    if message.receiver == request.user and not message.read:
        message.read = True
        message.save(update_fields=['read'])
    
    # Get all replies using the optimized get_thread method
    replies = message.get_thread()
    
    # Get edit history
    edit_history = MessageHistory.objects.filter(
        message=message
    ).select_related('edited_by').order_by('-edited_at')
    
    context = {
        'message': message,
        'replies': replies,
        'edit_history': edit_history
    }
    
    return render(request, 'messaging/message_detail.html', context)


@login_required
def send_message(request):
    """
    View to send a new message or reply to an existing message.
    """
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        parent_message_id = request.POST.get('parent_message_id')
        
        if not receiver_id or not content:
            django_messages.error(request, 'Receiver and content are required.')
            return redirect('inbox')
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        parent_message = None
        if parent_message_id:
            parent_message = get_object_or_404(Message, id=parent_message_id)
        
        # Create the message (signal will create notification automatically)
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        
        django_messages.success(request, 'Message sent successfully!')
        return redirect('message_detail', message_id=message.id)
    
    # GET request - show send message form
    users = User.objects.exclude(id=request.user.id)
    context = {'users': users}
    return render(request, 'messaging/send_message.html', context)


@login_required
def edit_message(request, message_id):
    """
    View to edit an existing message.
    Pre_save signal will log the edit automatically.
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is authorized to edit
    if message.sender != request.user:
        return HttpResponseForbidden("You can only edit your own messages.")
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content:
            message.content = new_content
            message.save()  # Signal will handle logging
            django_messages.success(request, 'Message edited successfully!')
            return redirect('message_detail', message_id=message.id)
    
    context = {'message': message}
    return render(request, 'messaging/edit_message.html', context)


@login_required
def notifications(request):
    """
    Display all notifications for the current user.
    """
    user_notifications = Notification.objects.filter(
        user=request.user
    ).select_related('message', 'message__sender').order_by('-timestamp')
    
    context = {
        'notifications': user_notifications,
        'unread_count': user_notifications.filter(read=False).count()
    }
    
    return render(request, 'messaging/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications')


@login_required
def threaded_conversation(request, message_id):
    """
    Display a threaded conversation starting from a specific message.
    Shows the parent and all nested replies efficiently.
    """
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )
    
    # Check authorization
    if root_message.sender != request.user and root_message.receiver != request.user:
        return HttpResponseForbidden("You don't have permission to view this conversation.")
    
    # Get all messages in the thread recursively
    def get_nested_replies(message):
        """Recursively get all replies with nested structure"""
        replies = message.get_thread()
        nested_structure = []
        for reply in replies:
            nested_structure.append({
                'message': reply,
                'replies': get_nested_replies(reply)
            })
        return nested_structure
    
    thread_structure = {
        'message': root_message,
        'replies': get_nested_replies(root_message)
    }
    
    context = {
        'root_message': root_message,
        'thread_structure': thread_structure
    }
    
    return render(request, 'messaging/threaded_conversation.html', context)
