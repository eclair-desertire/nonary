# Generated by Django 4.0.6 on 2022-09-30 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0043_alter_product_image_productimages'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductImages',
            new_name='ProductImage',
        ),
    ]
