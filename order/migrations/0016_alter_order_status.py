# Generated by Django 4.0.6 on 2022-11-18 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_alter_webkassatoken_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('not_finished', 'Не завершен'), ('new', 'Новый'), ('processing', 'В обработке'), ('in_stock', 'Комплектация'), ('staffed', 'Укомплектован на складе'), ('delivery_department', 'Передан в отдел доставки'), ('delivery_courier', 'Передан курьеру'), ('delivered', 'Доставлен'), ('completed', 'Выполнен'), ('canceled', 'Отменен')], default='new', max_length=20, verbose_name='Статус'),
        ),
    ]