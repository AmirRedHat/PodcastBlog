# Generated by Django 3.2.8 on 2021-10-23 15:59

from django.db import migrations, models
import podcast.models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0008_auto_20211023_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='file',
            field=models.FileField(upload_to='episodes/', validators=[podcast.models.file_validator]),
        ),
    ]