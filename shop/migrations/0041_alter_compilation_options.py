# Generated by Django 4.0.6 on 2022-09-12 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0040_alter_compilation_products'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compilation',
            options={'ordering': ('position',), 'verbose_name': 'Выборку', 'verbose_name_plural': 'Выборки'},
        ),
    ]