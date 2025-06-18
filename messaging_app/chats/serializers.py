# messaging_app/chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message, MessageReadStatus


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic information
    """
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
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with additional fields
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'sent_at',
            'is_read',
            'read_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']
    
    def create(self, validated_data):
        # Remove sender_id from validated_data and use it to set sender
        sender_id = validated_data.pop('sender_id')
        try:
            sender = User.objects.get(user_id=sender_id)
            validated_data['sender'] = sender
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender ID")
        
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages
    """
    message_body = serializers.CharField(required=True, max_length=1000)
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Conversation model
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    last_message = MessageSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'last_message',
            'message_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = super().create(validated_data)
        
        # Add participants to the conversation
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Conversation with nested messages
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = super().create(validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new conversations
    """
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of user IDs to include in the conversation"
    )
    
    class Meta:
        model = Conversation
        fields = ['participant_ids']
    
    def validate_participant_ids(self, value):
        """
        Validate that all participant IDs exist and are unique
        """
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate participant IDs are not allowed")
        
        existing_users = User.objects.filter(user_id__in=value)
        if existing_users.count() != len(value):
            missing_ids = set(value) - set(existing_users.values_list('user_id', flat=True))
            raise serializers.ValidationError(f"Users with IDs {list(missing_ids)} do not exist")
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        
        return conversation


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for message read status tracking
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['message', 'user', 'read_at']
        read_only_fields = ['read_at']