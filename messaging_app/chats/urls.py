"""
URL configuration for chats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Note: Messages are nested under conversations, so we'll handle that in a basic way (optional: use nested routers for better structure)

urlpatterns = [
    path('', include(router.urls)),
    # For flat message access, not nested (basic setup)
    path('conversations/<int:conversation_pk>/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='conversation-messages'),
]
