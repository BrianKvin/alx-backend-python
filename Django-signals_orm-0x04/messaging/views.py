from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Q
from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory


@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_list(request):
    """
    Display a list of conversations with caching.
    Cached for 60 seconds to improve performance.
    """
    # Get conversations where user is either sender or receiver
    messages_sent = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    messages_received = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    
    # Get unique users the current user has conversations with
    conversation_users = User.objects.filter(
        Q(id__in=messages_sent) | Q(id__in=messages_received)
    ).distinct()
    
    # Get latest message for each conversation
    conversations = []
    for user in conversation_users:
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) | 
            Q(sender=user, receiver=request.user)
        ).first()
        
        if latest_message:
            conversations.append({
                'user': user,
                'latest_message': latest_message,
                'unread_count': Message.unread_objects.filter(
                    sender=user, receiver=request.user
                ).count()
            })
    
    # Sort by latest message timestamp
    conversations.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)
    
    return render(request, 'chats/conversation_list.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail(request, user_id):
    """
    Display a detailed conversation with a specific user.
    Uses advanced ORM techniques for threaded conversations.
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Get all messages in this conversation with optimized queries
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related('sender', 'receiver', 'parent_message').prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver')),
        'edit_history'
    ).order_by('timestamp')
    
    # Separate thread starters from replies
    thread_starters = messages.filter(parent_message__isnull=True)
    
    # Mark messages as read
    Message.objects.filter(
        sender=other_user, 
        receiver=request.user, 
        read=False
    ).update(read=True)
    
    return render(request, 'chats/conversation_detail.html', {
        'other_user': other_user,
        'thread_starters': thread_starters,
        'messages': messages
    })


@login_required
def unread_messages(request):
    """
    Display only unread messages for the current user.
    Uses custom manager and optimization with .only()
    """
    # Use custom manager to get unread messages with only necessary fields
    unread_messages = Message.unread_objects.unread_for_user(request.user).only(
        'sender__username', 
        'content', 
        'timestamp', 
        'parent_message'
    ).select_related('sender')
    
    return render(request, 'chats/unread_messages.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_messages.count()
    })


@login_required
def message_history(request, message_id):
    """
    Display edit history for a specific message.
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, "You don't have permission to view this message history.")
        return redirect('conversation_list')
    
    # Get edit history
    history = MessageHistory.objects.filter(message=message).order_by('-edited_at')
    
    return render(request, 'chats/message_history.html', {
        'message': message,
        'history': history
    })


@login_required
def send_message(request):
    """
    Send a new message or reply to an existing message.
    """
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        parent_message_id = request.POST.get('parent_message_id')
        
        if receiver_id and content:
            receiver = get_object_or_404(User, id=receiver_id)
            parent_message = None
            
            if parent_message_id:
                parent_message = get_object_or_404(Message, id=parent_message_id)
            
            # Create new message
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                parent_message=parent_message
            )
            
            messages.success(request, "Message sent successfully!")
            return redirect('conversation_detail', user_id=receiver.id)
    
    return redirect('conversation_list')


@login_required
def edit_message(request, message_id):
    """
    Edit an existing message.
    """
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content:
            message.content = new_content
            message.save()  # This will trigger the pre_save signal
            messages.success(request, "Message updated successfully!")
    
    return redirect('conversation_detail', user_id=message.receiver.id)


@login_required
def delete_user_account(request):
    """
    Delete user account and all related data.
    This will trigger the post_delete signal.
    """
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if confirm == 'DELETE':
            user = request.user
            logout(request)  # Log out the user first
            user.delete()  # This triggers the post_delete signal
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('home')  # Redirect to home page
    
    return render(request, 'chats/delete_account.html')


@login_required
def notifications(request):
    """
    Display user notifications.
    """
    user_notifications = Notification.objects.filter(
        user=request.user
    ).select_related('message__sender').order_by('-created_at')
    
    return render(request, 'chats/notifications.html', {
        'notifications': user_notifications
    })


@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications')