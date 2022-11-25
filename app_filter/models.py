from django.db import models
from utils.models import BaseModel


class CategoryFilter(BaseModel):
    category = models.ForeignKey('shop.Subcategory', on_delete=models.CASCADE, related_name='filters',
                                 verbose_name='Категория 2-го уровня')
    name = models.CharField(max_length=1000)
    property = models.ForeignKey('shop.Property', on_delete=models.CASCADE, related_name='filters',
                                 verbose_name='Характеристика')

    def __str__(self):
        return f"{self.category.name} - {self.property.name}"

    class Meta:
        verbose_name = 'Фильтр'
        verbose_name_plural = 'Фильтры'
        ordering = ('position', )
