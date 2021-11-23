# Generated by Django 3.2.9 on 2021-11-23 02:40

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_memberof_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='location',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='radius',
        ),
        migrations.AddField(
            model_name='chat',
            name='polygon',
            field=django.contrib.gis.db.models.fields.PolygonField(geography=True, null=True, srid=4326),
        ),
    ]
