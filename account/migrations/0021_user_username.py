# Generated by Django 3.2.8 on 2021-11-08 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
