# Generated by Django 4.0.6 on 2022-08-02 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0010_alter_question_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badsms',
            name='position',
            field=models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция'),
        ),
        migrations.AlterField(
            model_name='question',
            name='position',
            field=models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция'),
        ),
        migrations.AlterField(
            model_name='usefulquestion',
            name='position',
            field=models.IntegerField(default=0, help_text='Для сортировки (по возрастанию)', verbose_name='Позиция'),
        ),
    ]
