# Generated by Django 4.0.6 on 2022-10-10 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_order_ordered_at_orderitem_product_original_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
