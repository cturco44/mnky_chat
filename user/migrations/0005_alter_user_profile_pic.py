# Generated by Django 3.2.9 on 2021-12-04 02:46

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(blank=True, default='default-profile.png', null=True, upload_to=user.models.get_file_path),
        ),
    ]