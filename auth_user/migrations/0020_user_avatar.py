# Generated by Django 4.0.6 on 2022-10-19 18:02

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0019_user_is_common'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='avatars', verbose_name='Аватар'),
        ),
    ]
