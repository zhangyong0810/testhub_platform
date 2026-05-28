from rest_framework import serializers
from .models import AssistantSession, AssistantMessage, KnowledgeBaseConfig, ChatMessage


class KnowledgeBaseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseConfig
        fields = ['id', 'kb_url', 'is_active', 'created_at', 'updated_at']


class AssistantSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantSession
        fields = ['id', 'session_id', 'title']
        read_only_fields = ['id']


class AssistantSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AssistantSession
        fields = ['id', 'session_id', 'title', 'user', 'user_name',
                  'message_count', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.chat_messages.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['created_at']


class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = ['id', 'message_type', 'content', 'created_at']
