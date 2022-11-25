from django.apps import apps
from django.utils.text import slugify
from transliterate import translit


def slugify_field(text: str, cls):
    app_label = 'shop'
    class_name = cls.__class__.__name__
    if class_name == 'City':
        app_label = 'location'
    my_string = translit(text, 'ru', reversed=True)
    slug = slugify(my_string.lower())
    if apps.get_model(app_label=app_label, model_name=class_name).objects.filter(slug=slug).exclude(pk=cls.pk).exists():
        slug = f"{slug}_{cls.pk}"
    return slug
