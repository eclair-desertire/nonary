from typing import OrderedDict

from django.apps import apps


def create_object(app_label, model_name, validated_data):
    return apps.get_model(app_label=app_label, model_name=model_name).objects.create(**validated_data)


def get_object_by_lookup(app_label, model_name, filter_lookup):
    ObjectModel = apps.get_model(app_label=app_label, model_name=model_name)
    try:
        return ObjectModel.objects.get(**filter_lookup)
    except ObjectModel.DoesNotExist:
        return None


def get_object_queryset(app_label, model_name, filter_lookup):
    return apps.get_model(app_label=app_label, model_name=model_name).objects.filter(**filter_lookup)


def update_object(instance, validated_data: OrderedDict):
    for key, value in validated_data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    instance.save()
    return instance


def change_is_active(instance):
    if hasattr(instance, 'is_active'):
        old = instance.is_active
        instance.is_active = not old
        instance.save()
    return instance


def delete_object(instance):
    instance.delete()
