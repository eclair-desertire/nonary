from django.conf import settings
from rest_framework import serializers

from utils.crud import get_object_queryset
from utils.current_site import get_current_domain_with_protocol
from utils.serializers import BaseSerializer


class ChatListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    is_open = serializers.BooleanField()
    author = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField()
    upload = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    def get_name(self, instance):
        if hasattr(instance, 'member_list') and len(instance.member_list) > 0:
            return instance.member_list[0].user.full_name
        return ''

    def get_is_online(self, instance):
        if hasattr(instance, 'member_list') and len(instance.member_list) > 0:
            return instance.member_list[0].user.is_online
        return False

    def get_avatar(self, instance):
        companion = self.context.get('companion')
        request = self.context.get('request')
        if request:
            current_domain = get_current_domain_with_protocol(request)
            if companion:
                avatar = companion.avatar
                if avatar:
                    return f"{current_domain}/{avatar.url}"
                return None
            for member in instance.member_list:
                if member.user != request.user:
                    avatar = member.user.avatar
                    if avatar:
                        return f"{current_domain}/{avatar.url}"
        return None

    def get_last_message(self, instance):
        return instance.message_list[0].text

    def get_upload(self, instance):
        if instance.message_list[0].upload:
            return f"{settings.CURRENT_SITE}{instance.message_list[0].upload.url}"
        return None

    def get_author(self, instance):
        companion = self.context.get('companion')
        request = self.context.get('request')
        if request:
            if companion:
                return companion.full_name
            for member in instance.member_list:
                if member.user != request.user:
                    return member.user.full_name
        return None

    def get_created_at(self, instance):
        return instance.message_list[0].created_at.isoformat()


class CreateMessageSerializer(BaseSerializer):
    chat = serializers.PrimaryKeyRelatedField(
        queryset=get_object_queryset('chat', 'Chat', {'is_open': True}),
        allow_null=True,
        required=False
    )
    text = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    upload = serializers.FileField(allow_null=True, required=False)


class CreateModeratorMessageSerializer(BaseSerializer):
    chat = serializers.PrimaryKeyRelatedField(
        queryset=get_object_queryset('chat', 'Chat', {'is_open': True}),
    )
    text = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    upload = serializers.FileField(allow_null=True, required=False)


class AuthorSerializer(BaseSerializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField()

    def get_full_name(self, instance):
        return instance.full_name


class MessageListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    author = AuthorSerializer()
    text = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    upload = serializers.FileField(allow_null=True, required=False)
    is_my = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_is_my(self, instance):
        request = self.context.get('request')
        if request:
            return request.user == instance.author
        return False


class MessageListQuerySerializer(BaseSerializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=get_object_queryset('chat', 'Chat', {}))
