# Generated by Django 4.0.6 on 2022-07-31 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный?')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('value', models.IntegerField(help_text='Значение в ТГ или в %', verbose_name='Значение скидки')),
                ('discount_type', models.CharField(choices=[('fix', 'Фикированное (тг)'), ('percent', 'Процентный (%)')], default='fix', help_text='Тип скидки - % или фиксированное значение', max_length=10, verbose_name='Тип скидки')),
                ('activate_from', models.DateField(blank=True, help_text='с какой даты можно вводить промокод и применить (включительно)', null=True, verbose_name='Применить с')),
                ('activate_to', models.DateField(blank=True, help_text='по какую дату можно вводить промокод и применить (включительно)', null=True, verbose_name='Применить по')),
                ('permanent', models.BooleanField(default=False, help_text='Если поставите галочку, то этот промокод будет действителен всегда. Даты будут игнорироваться', verbose_name='Всегда?')),
            ],
            options={
                'verbose_name': 'Промокод',
                'verbose_name_plural': 'Промокоды',
                'ordering': ('permanent', '-activate_to', '-activate_from', '-created_at'),
            },
        ),
    ]