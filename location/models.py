from django.db import models

from utils.choices import ObjectTypeChoices, AddressIconChoices
from utils.models import BaseModel, SlugModel


class City(SlugModel):
    storehouses = models.ManyToManyField('shop.Storehouse', verbose_name='Склады', related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class UserAddress(BaseModel):
    title = models.CharField(max_length=255)
    icon_enum = models.CharField(max_length=25, choices=AddressIconChoices.choices, default=AddressIconChoices.OTHER)
    street = models.TextField()
    office = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, related_name='addresses')
    user = models.ForeignKey('auth_user.User', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='addresses')

    @property
    def full_address(self):
        a = [self.city.name]
        if self.street:
            a.append(self.street)
        if self.office:
            a.append(f"кв. {self.office}")
        return ", ".join(a)

    @property
    def only_street(self):
        a = []
        if self.street:
            a.append(self.street)
        if self.office:
            a.append(f"кв. {self.office}")
        return ", ".join(a)

    def __str__(self):
        return f"{self.city.name}, {self.street}"


class Post(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='posts', verbose_name='Город')
    address = models.CharField(max_length=500, verbose_name='Адрес')
    latitude = models.FloatField(verbose_name='Широта')
    longitude = models.FloatField(verbose_name='Долгота')
    object_type = models.CharField(max_length=255, choices=ObjectTypeChoices.choices, default=ObjectTypeChoices.POST,
                                   verbose_name='Тип объекта')
    schedule = models.CharField(max_length=255, blank=True, default='', verbose_name='Расписание')
    commerceml_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место доставки ИД')

    @property
    def full_address(self):
        a = [self.city.name]
        if self.address:
            a.append(self.address)
        return ", ".join(a)

    @property
    def only_street(self):
        return self.address

    class Meta:
        verbose_name = 'Объект (Постамат, Пункт выдачи)'
        verbose_name_plural = 'Объекты (Постаматы, Пункты выдачи)'
