from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import ChatListView, CreateMessageView, CreateModeratorMessageView, MessageListView, CloseChatView

router = DefaultRouter()

router.register('chats', ChatListView, basename='chat-list')
router.register('messages-list', MessageListView, basename='message-list')
router.register('messages', CreateMessageView, basename='message-create')
router.register('moderator-messages', CreateModeratorMessageView, basename='moderator-message-create')


urlpatterns = [
    path('close-chat/<int:chat_id>/', CloseChatView.as_view(), name='close-chat'),
] + router.urls
