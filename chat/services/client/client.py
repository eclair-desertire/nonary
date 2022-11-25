from django.apps import apps
from django.db.models import Prefetch, Case, When, Value, BooleanField, Q, Count

from chat.services.common import create_chat_member
from utils.crud import create_object, get_object_queryset


ChatMember = apps.get_model(app_label='chat', model_name='ChatMember')


def _create_chat():
    return create_object('chat', 'Chat', {'is_open': True})


def create_message(validated_data, user):
    created = False
    if validated_data.get('chat', None) is None:
        chat = _create_chat()
        created = True
        create_chat_member(chat, user)
        validated_data.update({
            'chat': chat
        })
    message = create_object('chat', 'Message', {'author': user, **validated_data})
    message.chat.save()
    return message, created


def get_chat_list(user):
    filter_lookup = {
        'members__user': user
    }

    qs = get_object_queryset('chat', "Chat", filter_lookup).prefetch_related(
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


def get_message_queryset(user, chat):
    filter_query = Q(chat__members__user=user)
    if user.is_staff:
        filter_query = filter_query | Q(member_count__lte=1)
    filter_lookup = {
        'chat': chat
    }

    qs = get_object_queryset('chat', "Message", filter_lookup).annotate(
        member_count=Count('chat__members__user_id', distinct=True)
    ).select_related(
        'author', 'chat'
    ).filter(
        filter_query
    ).annotate(
        is_my=Case(
            When(
                author=user, then=Value(True, output_field=BooleanField())
            ), default=Value(False, output_field=BooleanField())
        )
    ).distinct().order_by('-created_at')

    return qs


def get_moderator(chat, current_user):
    member = ChatMember.objects.filter(chat=chat).exclude(user=current_user).select_related('user')
    if member.exists():
        return member.first().user
    return None

