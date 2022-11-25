# Generated by Django 4.0.6 on 2022-08-02 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo', '0004_promo_position_userselectedpromo_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo',
            name='position',
            field=models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция'),
        ),
        migrations.AlterField(
            model_name='userselectedpromo',
            name='position',
            field=models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция'),
        ),
    ]