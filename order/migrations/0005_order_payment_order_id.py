# Generated by Django 4.0.6 on 2022-08-31 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_remove_order_address_order_comment_order_delivery_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_order_id',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]