from django.apps import apps

FavouriteProduct = apps.get_model(app_label='auth_user', model_name='FavouriteProduct')
UserSeenProduct = apps.get_model(app_label='shop', model_name='UserSeenProduct')


def set_unset_favourite(instance, user):
    qs = FavouriteProduct.objects.filter(product=instance, user=user)
    if qs.exists():
        qs.delete()
    else:
        FavouriteProduct.objects.create(user=user, product=instance)


def set_seen_product(instance, user):
    if user.is_authenticated:
        UserSeenProduct.objects.create(product=instance, user=user)
