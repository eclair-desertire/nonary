# Generated by Django 4.0.6 on 2022-11-10 05:49

from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0055_product_image_url_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='image_url',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на картинку'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, help_text='больше не используется', null=True, upload_to='products', verbose_name='Картинка'),
        ),
    ]