# Generated by Django 3.2.9 on 2021-11-23 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_chat_radius'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='desciption',
            new_name='description',
        ),
    ]