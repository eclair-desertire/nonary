# Generated by Django 4.0.6 on 2022-09-15 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0041_alter_compilation_options'),
        ('location', '0017_alter_city_storehouses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='storehouses',
            field=models.ManyToManyField(related_name='cities', to='shop.storehouse', verbose_name='Склады'),
        ),
    ]
