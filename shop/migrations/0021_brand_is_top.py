# Generated by Django 4.0.6 on 2022-08-19 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_productreview_reviewuseful_reviewimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='is_top',
            field=models.BooleanField(default=False, verbose_name='В списке топ?'),
        ),
    ]
