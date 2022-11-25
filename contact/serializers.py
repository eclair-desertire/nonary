from rest_framework import serializers

from contact.models import AboutImage, About, Magazine, Requisite
from utils.serializers import BaseSerializer


class ContactListSerializer(BaseSerializer):
    name = serializers.CharField()
    link_type = serializers.CharField()
    link = serializers.CharField()
    position = serializers.IntegerField()


class PublicOfferListSerializer(BaseSerializer):
    content = serializers.CharField()


class AboutImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutImage
        exclude = ('about', )


class AboutSerializer(serializers.ModelSerializer):
    images = AboutImageSerializer(many=True)

    class Meta:
        model = About
        fields = '__all__'


class MagazineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Magazine
        fields = '__all__'


class RequisiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Requisite
        fields = '__all__'
