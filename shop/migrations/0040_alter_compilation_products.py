# Generated by Django 4.0.6 on 2022-09-12 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_alter_compilation_compilation_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compilation',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='compilations', to='shop.product', verbose_name='Товары'),
        ),
    ]