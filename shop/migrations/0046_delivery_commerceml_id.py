# Generated by Django 4.0.6 on 2022-10-04 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0045_alter_productimage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='commerceml_id',
            field=models.CharField(blank=True, help_text='Используется если доставка курьером', max_length=255, null=True, verbose_name='Место доставки ИД'),
        ),
    ]
