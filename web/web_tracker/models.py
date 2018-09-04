from django.db import models
from .validators import validate_reminder


# Create your models here.


class Task(models.Model):
    name = models.CharField(max_length=100)
    queue = models.CharField(max_length=30)
    description = models.TextField(default='')
    parent = models.CharField(max_length=30)
    sub_tasks = models.TextField(default='')
    related = models.CharField(max_length=30)
    author = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)
    start = models.CharField(max_length=30)
    deadline = models.CharField(max_length=30)
    tags = models.TextField(default='')
    reminder = models.TextField(
        default='',
        validators=[validate_reminder])
    status = models.CharField(max_length=30)
    key = models.CharField(max_length=30)
    creating_time = models.CharField(max_length=30)
    editing_time = models.CharField(max_length=30)
    responsible = models.TextField(default='')

    objects = models.Manager()


class Plan(models.Model):
    author = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=30, default='')
    time = models.CharField(max_length=30)
    reminder = models.TextField(default='')
    key = models.CharField(max_length=30)

    objects = models.Manager()


class Queue(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=30)
    owner = models.IntegerField(0)
    opened_tasks = models.TextField(default='')
    failed_tasks = models.TextField(default='')
    solved_tasks = models.TextField(default='')

    objects = models.Manager()
    # TODO: закончить модели


class User(models.Model):
    uid = models.IntegerField(0)
    nick = models.CharField(max_length=100)
    queues = models.TextField(default='')
    tasks_author = models.TextField(default='')
    tasks_responsible = models.TextField(default='')
    notifications = models.TextField(default='')
    new_messages = models.TextField(default='')
