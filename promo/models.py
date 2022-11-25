from django.contrib.auth import get_user_model
from django.db import models

from utils.choices import DiscountTypeChoices
from utils.models import BaseModel

User = get_user_model()


class Promo(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    value = models.IntegerField(verbose_name='Значение скидки', help_text='Значение в ТГ или в %')
    is_auto = models.BooleanField(default=True, verbose_name='Автоматический?')
    discount_type = models.CharField(max_length=10, choices=DiscountTypeChoices.choices,
                                     default=DiscountTypeChoices.FIXED, verbose_name='Тип скидки',
                                     help_text='Тип скидки - % или фиксированное значение')
    activate_from = models.DateField(verbose_name='Применить с', blank=True, null=True,
                                     help_text='с какой даты можно вводить промокод и применить (включительно)')

    activate_to = models.DateField(verbose_name='Применить по', blank=True, null=True,
                                   help_text='по какую дату можно вводить промокод и применить (включительно)')
    permanent = models.BooleanField(default=False, verbose_name='Всегда?',
                                    help_text='Если поставите галочку, то этот промокод будет действителен всегда. ' \
                                              'Даты будут игнорироваться')
    min_order_price = models.IntegerField(default=0)
    max_order_price = models.IntegerField(default=0)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ('-permanent', '-activate_to', '-activate_from', '-created_at')


class UserSelectedPromo(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promos')
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name='users')
    selected = models.BooleanField(default=False)
    