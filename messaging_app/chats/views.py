from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from django_filters.rest_framework import DjangoFilterBackend 
from .filters import ConversationFilter, MessageFilter 
from django.db import models 

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'conversation_id'
    filter_backends = [DjangoFilterBackend] 
    filterset_class = ConversationFilter 

    def get_queryset(self):
        """
        Filter conversations to only show those the user is participating in
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.order_by('-sent_at')[:10])
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add the current user to participants if not already included
        participant_ids = list(serializer.validated_data['participant_ids']) # Ensure it's a list
        if request.user.user_id not in participant_ids:
            participant_ids.append(request.user.user_id)

        # Check if a conversation with the same participants already exists
        existing_conversation = None
        if len(participant_ids) == 2:
            # For two-person conversations, check if one already exists
            existing_conversation = Conversation.objects.filter(
                participants__user_id__in=participant_ids
            ).annotate(
                participant_count=models.Count('participants')
            ).filter(
                participant_count=2
            ).first()

        if existing_conversation:
            response_serializer = ConversationSerializer(existing_conversation)
            return Response(
                {
                    'message': 'Conversation already exists',
                    'conversation': response_serializer.data
                },
                status=status.HTTP_200_OK
            )

        conversation = serializer.save()
        response_serializer = ConversationSerializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_message(self, request, conversation_id=None):
        """
        Send a message to a specific conversation
        """
        conversation = self.get_object()

        # Check if user is a participant in the conversation
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=serializer.validated_data['message_body']
        )

        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_conversations(self, request):
        """
        Get all conversations for the current user
        """
        conversations = self.get_queryset()
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'message_id'
    filter_backends = [DjangoFilterBackend] # Add this
    filterset_class = MessageFilter # Add this

    def get_queryset(self):
        """
        Filter messages to only show those in conversations the user participates in
        """
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data['conversation']

        # Check if user is a participant in the conversation
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=serializer.validated_data['message_body']
        )

        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, message_id=None):
        """
        Mark a message as read
        """
        message = self.get_object()

        # Only allow marking as read if user is in the conversation but not the sender
        if message.sender == request.user:
            return Response(
                {'error': 'Cannot mark your own message as read'},
                status=status.HTTP_400_BAD_REQUEST
            )

        message.mark_as_read()
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get all unread messages for the current user
        """
        unread_messages = self.get_queryset().filter(
            is_read=False
        ).exclude(sender=request.user)

        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)

  