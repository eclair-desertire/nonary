# Generated by Django 4.0.6 on 2022-08-02 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]