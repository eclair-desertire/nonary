from rest_framework import serializers

from location.services.client.querysets import get_city_queryset
from utils.choices import AddressIconChoices
from utils.serializers import BaseSerializer
from django.apps import apps


UserAddress = apps.get_model(app_label='location', model_name='UserAddress')


class AddressCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ('is_active', 'user', 'created_at', 'updated_at')
        
    def to_representation(self, instance):
        return super(AddressCreateUpdateSerializer, self).to_representation(instance)


class AddressListSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    street = serializers.CharField(read_only=True)
    office = serializers.CharField(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    city_name = serializers.SerializerMethodField()
    city_slug = serializers.SerializerMethodField()
    icon_enum = serializers.ChoiceField(choices=AddressIconChoices.choices)

    def get_city_name(self, instance):
        if instance.city is not None:
            return instance.city.name
        return None

    def get_city_slug(self, instance):
        if instance.city is not None:
            return instance.city.slug
        return None


class PostSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    schedule = serializers.CharField()


class PostFilterSerializer(BaseSerializer):
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    radius = serializers.FloatField(required=False)


class SelectCitySerializer(BaseSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=get_city_queryset({'is_active': True}))


class PostQuerySerializer(BaseSerializer):
    city_slug = serializers.CharField()


class CityWithAddressSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    address_list = AddressListSerializer(many=True)


class YandexResponseSerializer(BaseSerializer):
    country = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    house = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    city_id = serializers.IntegerField()
