from django_filters import rest_framework as filters

from auth_user.models import Question


class QuestionFilter(filters.FilterSet):

    class Meta:
        model = Question
        fields = ['category']
