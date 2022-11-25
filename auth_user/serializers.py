from django.apps import apps

from auth_user.models import UserCard
from auth_user.services.client.queryset import get_question_queryset
from utils.serializers import BaseSerializer
from rest_framework import serializers


class UserAuthSerializer(BaseSerializer):
    phone_number = serializers.RegexField(r'^\+\d{1,1}\d{1,4}(?!0)\d{1,10}\b')


class ChooseCardSerializer(BaseSerializer):
    card = serializers.PrimaryKeyRelatedField(queryset=UserCard.objects.all())


class UserCardListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    pan = serializers.CharField()
    brand = serializers.CharField()
    card_token = serializers.CharField()
    is_selected = serializers.BooleanField()


class CitySerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    has_delivery = serializers.BooleanField()


class UserCitySerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()


class ProfileSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.RegexField(r'^\+\d{1,1}\d{1,4}(?!0)\d{1,10}\b', read_only=True)
    city = UserCitySerializer()


class ProfileEditSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UpdateUserCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = apps.get_model(app_label='auth_user', model_name='User')
        fields = ('city', )


class UpdateUserEmailSerializer(BaseSerializer):
    email = serializers.EmailField()


class ChangeEmailTokenSerializer(BaseSerializer):
    token = serializers.CharField()


class ChangeEmailCodeSerializer(BaseSerializer):
    verification_code = serializers.CharField()


class LoginSerializer(BaseSerializer):
    token = serializers.CharField()
    verification_code = serializers.CharField()


class ProfileWithTokenSerializer(BaseSerializer):
    token = serializers.CharField()
    user = ProfileSerializer()


class QuestionCategoryListSerializer(BaseSerializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    icon = serializers.ImageField()


class QuestionListSerializer(BaseSerializer):
    question = serializers.CharField()
    answer = serializers.CharField()
    updated_at = serializers.DateTimeField()
    answered = serializers.BooleanField()


class UsefulQuestionSerializer(BaseSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=get_question_queryset({}))
    is_useful = serializers.BooleanField()


class FavouriteCountSerializer(BaseSerializer):
    favourite_count = serializers.IntegerField()


class CardRegistrationURLSerializer(BaseSerializer):
    url = serializers.URLField()


class DeleteCardTokenSerializer(BaseSerializer):
    card = serializers.PrimaryKeyRelatedField(queryset=UserCard.objects.all())