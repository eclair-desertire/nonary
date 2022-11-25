from django.apps import apps
from django.db.models import Prefetch, Q, Count

from chat.services.common import create_chat_member, send_to_channel
from utils.crud import create_object, get_object_queryset


def create_moderator_message(validated_data, user):
    create_chat_member(validated_data.get('chat'), user)
    message = create_object('chat', 'Message', {'author': user, **validated_data})
    message.chat.save()
    return message


def get_moderator_chat_list(user=None, chat_id=None):
    filter_kwargs = {}
    if chat_id:
        filter_kwargs.update({
            'id': chat_id
        })
    additional_filter = Q(member_count__lte=1)
    if user is not None:
        additional_filter = additional_filter | Q(members__user=user)
    qs = apps.get_model('chat', "Chat").objects.annotate(
        member_count=Count('members__user_id', distinct=True)
    ).filter(
        additional_filter, **filter_kwargs
    ).prefetch_related(
        Prefetch(
            'messages',
            queryset=apps.get_model('chat', 'Message').objects.order_by('-created_at'),
            to_attr='message_list'
        ),
        Prefetch(
            'members',
            queryset=apps.get_model('chat', 'ChatMember').objects.select_related('user'),
            to_attr='member_list'
        )
    ).distinct().order_by('-updated_at')

    return qs


def close_chat(chat_id):
    apps.get_model('chat', "Chat").objects.filter(id=chat_id).update(is_open=False)
