# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-03 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_tracker', '0003_auto_20180903_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='progress',
            field=models.IntegerField(default=0),
        ),
    ]
