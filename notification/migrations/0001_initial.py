# Generated by Django 4.0.6 on 2022-07-31 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный?')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Сообщение')),
                ('image', models.ImageField(blank=True, null=True, upload_to='notification/', verbose_name='Картинка')),
            ],
            options={
                'verbose_name': 'Пуш уведомление',
                'verbose_name_plural': 'Пуш уведомления',
                'ordering': ('-created_at',),
            },
        ),
    ]