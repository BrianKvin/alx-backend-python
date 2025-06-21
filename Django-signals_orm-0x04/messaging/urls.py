from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversation/<int:user_id>/', views.conversation_detail, name='conversation_detail'),
    path('unread/', views.unread_messages, name='unread_messages'),
    path('message/<int:message_id>/history/', views.message_history, name='message_history'),
    path('send/', views.send_message, name='send_message'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('delete-account/', views.delete_user_account, name='delete_user_account'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]