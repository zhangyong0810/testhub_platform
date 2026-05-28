from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
import requests
from .models import AssistantSession, ChatMessage, KnowledgeBaseConfig
from .serializers import (
    AssistantSessionSerializer,
    AssistantSessionCreateSerializer,
    ChatMessageSerializer
)


class AssistantSessionViewSet(viewsets.ModelViewSet):
    """智能助手会话视图集"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssistantSessionCreateSerializer
        return AssistantSessionSerializer

    def get_queryset(self):
        return AssistantSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的聊天消息"""
        session = self.get_object()
        messages = session.chat_messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatViewSet(viewsets.ViewSet):
    """聊天功能 - 连接到本地知识库"""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """发送消息到本地知识库"""
        session_id = request.data.get('session_id')
        message = request.data.get('message')

        if not session_id or not message:
            return Response(
                {'error': 'session_id和message都是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取会话
        try:
            session = AssistantSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except AssistantSession.DoesNotExist:
            return Response(
                {'error': '会话不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 获取知识库配置
        kb_config = KnowledgeBaseConfig.get_active_config()
        if not kb_config or not kb_config.kb_url:
            return Response(
                {'error': '未配置本地知识库，请先在配置中心配置AI评测师'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 保存用户消息
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )

        try:
            # 调用本地知识库 API
            kb_url = kb_config.kb_url.rstrip('/')
            response = requests.post(
                f'{kb_url}/ask',
                json={'question': message, 'user_id': str(request.user.id)},
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                source = data.get('source', 'unknown')
                references = data.get('references', [])

                # 构建带来源信息的回答
                if references and source != 'standard_answer':
                    ref_text = '\n\n---\n相关来源：\n' + '\n'.join(
                        f"{i+1}. {r['file']} (匹配度: {r['score']})"
                        for i, r in enumerate(references)
                    )
                    answer = answer + ref_text

                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=answer
                )

                return Response({
                    'user_message': ChatMessageSerializer(user_message).data,
                    'assistant_message': ChatMessageSerializer(assistant_message).data,
                    'source': source,
                    'references': references
                })
            else:
                return Response({
                    'error': f'知识库错误: {response.status_code}',
                    'detail': response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.Timeout:
            return Response({
                'error': '知识库请求超时'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            return Response({
                'error': f'请求失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def assistant_view(request):
    """智能助手页面视图 - 用于iframe内嵌"""
    return render(request, 'assistant/assistant.html')
