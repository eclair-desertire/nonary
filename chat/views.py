from django.apps import apps

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser

from chat.serializers import ChatListSerializer, CreateMessageSerializer, MessageListSerializer, \
    CreateModeratorMessageSerializer, MessageListQuerySerializer
from chat.services.client.client import get_chat_list, create_message, get_message_queryset, get_moderator
from chat.services.common import send_to_channel, send_to_global, send_to_client_global
from chat.services.moderator.moderator import create_moderator_message, get_moderator_chat_list, close_chat
from utils.manual_parameters import QUERY_CHAT


class ChatListView(ListModelMixin, GenericViewSet):
    serializer_class = ChatListSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter, )
    search_fields = (
        'messages__text', 'messages__author__first_name', 'messages__author__last_name', 'messages__author__middle_name'
    )

    def get_queryset(self):
        if self.request.user.is_staff:
            return get_moderator_chat_list(user=self.request.user)
        return get_chat_list(self.request.user)


class MessageListView(ListModelMixin, GenericViewSet):
    serializer_class = MessageListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        serializer = MessageListQuerySerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return get_message_queryset(self.request.user, serializer.validated_data.get('chat'))

    @swagger_auto_schema(
        manual_parameters=[QUERY_CHAT]
    )
    def list(self, request, *args, **kwargs):
        return super(MessageListView, self).list(request, *args, **kwargs)


class CreateMessageView(CreateModelMixin, GenericViewSet):
    serializer_class = CreateMessageSerializer
    queryset = apps.get_model(app_label='chat', model_name='Message').objects.none()
    permission_classes = (IsAuthenticated, )
    parser_classes = (MultiPartParser, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance, created = create_message(serializer.validated_data, self.request.user)
        chat_id = instance.chat_id
        instance.chat.save()
        context = self.get_serializer_context()
        context.update({'companion': None})
        message = MessageListSerializer(instance, context=context).data
        moderator_context = context.copy()
        moderator_context.update({'companion': request.user})
        moderator_message = MessageListSerializer(instance, context=moderator_context).data
        message.update({
            'is_my': True
        })
        send_to_channel(chat_id, message, channel_prefix='client')
        moderator_message.update({
            'is_my': False
        })
        send_to_channel(chat_id, moderator_message)
        if created:
            chat_qs = get_moderator_chat_list(user=None, chat_id=instance.chat_id)
        else:
            moderator = get_moderator(instance.chat, request.user)
            if moderator:
                chat_qs = get_moderator_chat_list(user=moderator, chat_id=instance.chat_id)
            else:
                chat_qs = get_moderator_chat_list(user=None, chat_id=instance.chat_id)

        send_to_global(ChatListSerializer(chat_qs.first(), context=moderator_context).data)
        client_chat_qs = get_chat_list(request.user)
        send_to_client_global(ChatListSerializer(client_chat_qs.first(), context=context).data, request.user.id)
        return Response({'message': 'created', 'chat_id': instance.chat_id})


class CreateModeratorMessageView(CreateMessageView):
    serializer_class = CreateModeratorMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_moderator_message(serializer.validated_data, self.request.user)

        chat_id = instance.chat_id
        instance.chat.save()

        context = self.get_serializer_context()
        moderator_companion = request.user
        context.update({
            'companion': None,
        })
        message = MessageListSerializer(instance, context=context).data
        client_context = context.copy()
        client_context.update({'companion': moderator_companion})
        client_message = MessageListSerializer(instance, context=client_context).data
        client_message.update({
            'is_my': False
        })
        send_to_channel(chat_id, client_message, channel_prefix='client')
        message.update({
            'is_my': True
        })
        send_to_channel(chat_id, message)
        client = get_moderator(instance.chat, request.user)
        moderator_chat_qs = get_chat_list(request.user)
        send_to_global(ChatListSerializer(moderator_chat_qs.first(), context=context).data)
        if client:
            client_chat_qs = get_chat_list(client)
            send_to_client_global(ChatListSerializer(client_chat_qs.first(), context=context).data, client.id)
        return Response({'message': 'created'})


@login_required(login_url='/admin/login/?next=/admin/')
def open_chat(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    return redirect(f'/chat/#/{token.key}')


class CloseChatView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, chat_id):
        close_chat(chat_id)
        return Response(status=HTTP_204_NO_CONTENT)
