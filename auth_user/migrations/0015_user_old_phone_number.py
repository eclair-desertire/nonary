# Generated by Django 4.0.6 on 2022-08-25 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0014_alter_questioncategory_icon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='old_phone_number',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]