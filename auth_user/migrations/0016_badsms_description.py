# Generated by Django 4.0.6 on 2022-08-30 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0015_user_old_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='badsms',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
