# Generated by Django 4.0.6 on 2022-07-31 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='image',
            new_name='upload',
        ),
    ]