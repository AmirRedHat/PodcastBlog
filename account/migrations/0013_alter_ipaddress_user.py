# Generated by Django 3.2.7 on 2021-09-04 04:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_ipaddress_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddress',
            name='user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ipaddress_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
