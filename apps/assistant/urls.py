from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssistantSessionViewSet, ChatViewSet, assistant_view
from .views_config import KnowledgeBaseConfigViewSet

router = DefaultRouter()
router.register(r'sessions', AssistantSessionViewSet, basename='assistant-session')
router.register(r'config', KnowledgeBaseConfigViewSet, basename='knowledge-base-config')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/send_message/', ChatViewSet.as_view({'post': 'send_message'}), name='chat-send-message'),
    path('view/', assistant_view, name='assistant-view'),
]
