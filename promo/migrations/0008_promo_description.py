# Generated by Django 4.0.6 on 2022-11-09 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo', '0007_promo_max_order_price_promo_min_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='promo',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
