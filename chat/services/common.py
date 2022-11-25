from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from utils.crud import create_object, get_object_queryset


def create_chat_member(chat, user):
    chat_members = get_object_queryset('chat', 'ChatMember', {'user': user, 'chat': chat})
    if not chat_members.exists():
        create_object('chat', 'ChatMember', {'user': user, 'chat': chat})


def send_to_channel(chat_id, message_data, channel_prefix='moderator'):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'{channel_prefix}_{chat_id}',
        {
            'type': 'chat_message',
            'message': message_data,
        }
    )


def send_to_client_global(chat_data, client_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'client_global_{client_id}',
        {
            'type': 'chat_message',
            'message': chat_data,
        }
    )


def send_to_global(chat_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'global',
        {
            'type': 'chat_message',
            'message': chat_data,
        }
    )
