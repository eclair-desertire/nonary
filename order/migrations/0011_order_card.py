# Generated by Django 4.0.6 on 2022-10-13 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0019_user_is_common'),
        ('order', '0010_order_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='card',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth_user.usercard'),
        ),
    ]
