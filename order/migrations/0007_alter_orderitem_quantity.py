# Generated by Django 4.0.6 on 2022-10-03 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_original_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='Количество'),
        ),
    ]
