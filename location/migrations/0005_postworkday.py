# Generated by Django 4.0.6 on 2022-07-28 02:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0004_remove_city_deleted_remove_post_deleted_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostWorkday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный?')),
                ('weekday', models.CharField(choices=[('sun', 'Воскресенье'), ('mon', 'Понедельник'), ('tue', 'Вторник'), ('wed', 'Среда'), ('thu', 'Четверг'), ('fri', 'Пятница'), ('sat', 'Суббота')], default='sun', max_length=5, verbose_name='День недели')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Время начало работы')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='Время завершения работы')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='location.post', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Расписание объекта',
                'verbose_name_plural': 'Расписании объектов',
                'unique_together': {('weekday', 'post')},
            },
        ),
    ]
