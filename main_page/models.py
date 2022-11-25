from django.db import models
from imagekit.models import ProcessedImageField

from utils.choices import StoryTypeChoices, LinkTypeChoices
from utils.models import BaseModel


class Stock(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    deadline = models.DateTimeField(verbose_name='Активен до', help_text='После этой даты акция скроется с приложения')
    image = ProcessedImageField(upload_to='stock', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True)

    products = models.ManyToManyField('shop.Product', related_name='stocks', blank=True)

    @property
    def short_description(self):
        return self.description if len(self.description) < 35 else (self.description[:33] + '..')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'


class Story(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')
    story_file = models.FileField(upload_to='story/', verbose_name='Файл', help_text='фото или видео')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    deeplink = models.TextField(blank=True, null=True, verbose_name='Ссылка для перехода в приложений')
    deadline = models.DateTimeField(verbose_name='Активен до', help_text='После этой даты стори скроется с приложения')
    story_type = models.CharField(max_length=50, choices=StoryTypeChoices.choices, default=StoryTypeChoices.NORMAL,
                                  verbose_name='Тип')

    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Акция')
    category = models.ForeignKey('shop.Subcategory', on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name='Категория 2-го уровня')
    brand = models.ForeignKey('shop.Brand', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Бренд')
    child_category = models.ForeignKey('shop.ChildCategory', on_delete=models.CASCADE, blank=True, null=True,
                                       verbose_name='Тип')
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Товар')
    info = models.ForeignKey('contact.Magazine', on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name='Tvoy.kz журнал')
    link_type = models.CharField(max_length=55, choices=LinkTypeChoices.choices, default=LinkTypeChoices.BLANK,
                                 verbose_name='Тип ссылки')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сториз и Баннер'
        verbose_name_plural = 'Сторизы и Баннеры'


class UserViewedStory(BaseModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='viewed_users')
    user = models.ForeignKey('auth_user.User', on_delete=models.CASCADE, related_name='viewed_stories')

