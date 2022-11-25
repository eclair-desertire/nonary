from rest_framework import serializers

from contact.models import Magazine
from main_page.models import Stock
from utils.serializers import BaseSerializer


class StockListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    deadline = serializers.DateTimeField()
    title = serializers.CharField()
    image = serializers.ImageField()


class StockSerializer(StockListSerializer):
    description = serializers.CharField()
    product_count = serializers.IntegerField()


class StorySerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    deadline = serializers.DateTimeField()
    story_file = serializers.FileField()
    link = serializers.URLField()
    deeplink = serializers.CharField()
    category_slug = serializers.CharField()
    brand_slug = serializers.CharField()
    child_category_slug = serializers.CharField()
    product_slug = serializers.CharField()
    link_type = serializers.CharField()
    info_id = serializers.IntegerField()
    stock_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
