# Generated by Django 4.0.6 on 2022-09-23 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0019_post_schedule_delete_postworkday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='office',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
