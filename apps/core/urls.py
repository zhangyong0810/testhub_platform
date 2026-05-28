"""
Core 应用路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UnifiedNotificationConfigViewSet, GenerationBehaviorConfigViewSet

router = DefaultRouter()
router.register(r'notification-configs', UnifiedNotificationConfigViewSet, basename='unified-notification-config')
router.register(r'behavior-configs', GenerationBehaviorConfigViewSet, basename='generation-behavior-config')

urlpatterns = [
    path('', include(router.urls)),
]
