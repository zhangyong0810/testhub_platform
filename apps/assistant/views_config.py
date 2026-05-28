from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import KnowledgeBaseConfig
from .serializers import KnowledgeBaseConfigSerializer
import requests


class KnowledgeBaseConfigViewSet(viewsets.ModelViewSet):
    """知识库配置管理"""
    queryset = KnowledgeBaseConfig.objects.all()
    serializer_class = KnowledgeBaseConfigSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        active_config = KnowledgeBaseConfig.get_active_config()
        if active_config:
            serializer = self.get_serializer(active_config)
            return Response(serializer.data)
        return Response({'message': '未找到激活的配置'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if request.data.get('is_active', True):
            KnowledgeBaseConfig.objects.update(is_active=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, partial=False):
        instance = self.get_object()
        if request.data.get('is_active', False):
            KnowledgeBaseConfig.objects.exclude(pk=pk).update(is_active=False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk, partial=True)

    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        kb_url = request.data.get('kb_url', '').rstrip('/')
        if not kb_url:
            return Response(
                {'error': '知识库URL是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = requests.get(f'{kb_url}/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return Response({
                    'message': f'连接成功！({data.get("docs_indexed", 0)}文档索引, {data.get("standard_answers", 0)}标准答案)',
                    'success': True,
                    'detail': data
                })
            return Response({
                'error': f'连接失败: {response.status_code}',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.Timeout:
            return Response({
                'error': '连接超时，请检查知识库URL是否正确',
                'success': False
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            return Response({
                'error': f'连接错误: {str(e)}',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
