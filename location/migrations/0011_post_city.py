# Generated by Django 4.0.6 on 2022-08-12 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0010_alter_city_position_alter_post_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='location.city', verbose_name='Город'),
            preserve_default=False,
        ),
    ]
