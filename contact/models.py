from django.db import models
from imagekit.models import ProcessedImageField

from utils.choices import ContactLinkChoices
from utils.models import BaseModel


class Contact(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')
    link_type = models.CharField(max_length=5, choices=ContactLinkChoices.choices, default=ContactLinkChoices.PHONE,
                                 verbose_name='Тип контакта')
    link = models.CharField(max_length=1000, verbose_name='Значение')

    def __str__(self):
        return f"{self.name} ({self.get_link_type_display()})"

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ('position', )


class PublicOffer(BaseModel):
    content = models.TextField()

    class Meta:
        verbose_name = 'Публичная оферта'
        verbose_name_plural = 'Публичные оферты'
        ordering = ('position', )


class Magazine(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField()
    image = ProcessedImageField(upload_to='magazine', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True, verbose_name='Картинка')

    @property
    def short_content(self):
        return self.content if len(self.content) < 35 else (self.content[:33] + '..')

    def __str__(self):
        return f"{self.title}  -  {self.created_at}"

    class Meta:
        verbose_name = 'Tvoy.kz Журнал'
        verbose_name_plural = 'Tvoy.kz Журнал'
        ordering = ('-is_active', '-created_at', )


class About(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок',
                             help_text='в дизайне это `Добро пожаловать в магазин Tvoy.kz`')
    content = models.TextField(verbose_name='Контент')
    
    def save(self, *args, **kwargs):
        if self.is_active:
            About.objects.filter(is_active=True).update(is_active=False)
        super(About, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}  -  {self.created_at}"

    class Meta:
        verbose_name = 'О нас'
        verbose_name_plural = 'О нас'
        ordering = ('-is_active', '-created_at', )


class AboutImage(BaseModel):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name='images', verbose_name='Контент')
    image = ProcessedImageField(upload_to='about', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True, verbose_name='Картинка')

    class Meta:
        verbose_name = 'Картинку (О нас)'
        verbose_name_plural = 'Картинки (О нас)'
        ordering = ('position', )


class Requisite(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')
    value = models.CharField(max_length=255, verbose_name='Значение')

    class Meta:
        verbose_name = 'Реквизит'
        verbose_name_plural = 'Реквизиты'
        ordering = ('position', )

    def __str__(self):
        return f"{self.name} {self.value}"

