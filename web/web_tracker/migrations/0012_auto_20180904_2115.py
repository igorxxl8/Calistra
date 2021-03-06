# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-04 18:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_tracker', '0011_plan_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='key',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='plan',
            name='period',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='queue',
            name='key',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='key',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='parent',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='queue',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='related',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='responsible',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='sub_tasks',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='task',
            name='tags',
            field=models.TextField(default=''),
        ),
    ]
