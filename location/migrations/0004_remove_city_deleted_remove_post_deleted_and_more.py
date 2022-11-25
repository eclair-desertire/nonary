# Generated by Django 4.0.6 on 2022-07-28 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='post',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='deleted',
        ),
        migrations.AddField(
            model_name='city',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активный?'),
        ),
        migrations.AddField(
            model_name='post',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активный?'),
        ),
        migrations.AddField(
            model_name='useraddress',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активный?'),
        ),
    ]
