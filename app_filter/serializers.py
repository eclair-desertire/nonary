from rest_framework import serializers
from utils.serializers import BaseSerializer


class FilterListSerializer(BaseSerializer):
    name = serializers.CharField()
    position = serializers.IntegerField()
    slug = serializers.SerializerMethodField()

    def get_slug(self, instance):
        return instance.property.slug
