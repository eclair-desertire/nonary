from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_queryset(kwargs):
    return User.objects.filter(**kwargs)
