# Generated by Django 4.0.6 on 2022-11-08 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0053_remove_productproperty_property_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='propertyvalue',
            options={'verbose_name': 'Значение характеристики', 'verbose_name_plural': 'Значения характеристик'},
        ),
    ]
