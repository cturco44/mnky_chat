# Generated by Django 3.2.9 on 2021-12-04 02:46

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.get_file_path),
        ),
    ]
