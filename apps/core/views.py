"""
Core 应用视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import UnifiedNotificationConfig, GenerationBehaviorConfig
from .serializers import UnifiedNotificationConfigSerializer, GenerationBehaviorConfigSerializer

import logging
logger = logging.getLogger(__name__)


class UnifiedNotificationConfigViewSet(viewsets.ModelViewSet):
    """统一通知配置视图集"""
    queryset = UnifiedNotificationConfig.objects.all()
    serializer_class = UnifiedNotificationConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['config_type', 'is_default', 'is_active']
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """创建通知配置"""
        instance = serializer.save(created_by=self.request.user)
        logger.info(f"创建统一通知配置: {instance.name}")

    def perform_update(self, serializer):
        """更新通知配置"""
        instance = serializer.save()
        logger.info(f"更新统一通知配置: {instance.name}")

    def perform_destroy(self, instance):
        """删除通知配置"""
        logger.info(f"删除统一通知配置: {instance.name}")
        instance.delete()

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认配置"""
        config = self.get_object()
        # 取消其他默认配置
        UnifiedNotificationConfig.objects.filter(is_default=True).update(is_default=False)
        # 设置当前为默认
        config.is_default = True
        config.save()
        return Response({'message': '已设置为默认配置'})

    @action(detail=False, methods=['get'])
    def active_configs(self, request):
        """获取所有启用的配置"""
        configs = UnifiedNotificationConfig.objects.filter(is_active=True)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)


class GenerationBehaviorConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """AI 生成行为配置视图集 (只读)"""
    queryset = GenerationBehaviorConfig.objects.filter(is_active=True)
    serializer_class = GenerationBehaviorConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['config_type', 'is_active']
    search_fields = ['name', 'description', 'config_key']
    ordering_fields = ['config_type', 'updated_at']
    ordering = ['config_type']

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按类型分组获取配置"""
        configs = GenerationBehaviorConfig.objects.filter(is_active=True)
        grouped = {}
        for c in configs:
            grouped.setdefault(c.get_config_type_display(), []).append(
                GenerationBehaviorConfigSerializer(c).data
            )
        return Response(grouped)
