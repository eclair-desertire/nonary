# Generated by Django 4.0.6 on 2022-09-22 06:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0016_badsms_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный?')),
                ('position', models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция')),
                ('pan', models.CharField(max_length=250)),
                ('brand', models.CharField(blank=True, max_length=250)),
                ('card_token', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]