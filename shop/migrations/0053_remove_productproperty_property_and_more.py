# Generated by Django 4.0.6 on 2022-11-08 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0052_property_is_multiple'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productproperty',
            name='property',
        ),
        migrations.RemoveField(
            model_name='productproperty',
            name='value',
        ),
        migrations.CreateModel(
            name='PropertyValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, default='', max_length=1000, null=True, verbose_name='Значение')),
                ('hex_value', models.CharField(blank=True, help_text='Если нужно отрисовать цвет!', max_length=25, null=True, verbose_name='Значение цвета')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='shop.property', verbose_name='Характеристика')),
            ],
        ),
        migrations.AddField(
            model_name='productproperty',
            name='property_value',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shop.propertyvalue', verbose_name='Значение характеристики'),
        ),
    ]
