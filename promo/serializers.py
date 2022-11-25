from rest_framework import serializers

from promo.models import Promo
from utils.crud import get_object_queryset
from utils.serializers import BaseSerializer


class SelectedPromoSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    selected = serializers.BooleanField()


class PromoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promo
        fields = '__all__'


class AddPromoSerializer(BaseSerializer):
    name = serializers.CharField()


class SelectPromoSerializer(BaseSerializer):
    promo = serializers.PrimaryKeyRelatedField(
        queryset=get_object_queryset('promo', 'Promo', {})
    )
