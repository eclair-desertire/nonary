from django.db.models import Prefetch

from utils.crud import get_object_queryset


def get_contact_queryset():
    return get_object_queryset('contact', 'Contact', {'is_active': True})


def get_public_offer_queryset():
    return get_object_queryset('contact', 'PublicOffer', {'is_active': True})


def get_magazine_queryset():
    return get_object_queryset('contact', 'Magazine', {'is_active': True})


def get_requisite_queryset():
    return get_object_queryset('contact', 'Requisite', {'is_active': True})


def get_about_las_active():
    return get_object_queryset('contact', 'About', {'is_active': True}).prefetch_related(
        Prefetch(
            'images',
            queryset=get_object_queryset('contact', 'AboutImage', {'is_active': True}).order_by('position')
        )
    ).distinct()
