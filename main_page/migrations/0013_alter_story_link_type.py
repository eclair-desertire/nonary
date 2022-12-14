# Generated by Django 4.0.6 on 2022-10-03 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0012_story_link_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='link_type',
            field=models.CharField(choices=[('blank', 'Без ссылки'), ('stock', 'Переход в акцию'), ('product_card', 'Переход в карточку товара'), ('category', 'Переход в категорию фильтрованую по бренду, типу'), ('magazine', 'Tvoy.kz журнал')], default='blank', max_length=55, verbose_name='Тип ссылки'),
        ),
    ]
