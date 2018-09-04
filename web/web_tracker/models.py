from django.db import models


# Create your models here.


class Task(models.Model):
    name = models.CharField(max_length=100)
    queue = models.CharField(max_length=10)
    description = models.TextField(default='')
    parent = models.CharField(max_length=10)
    sub_tasks = models.TextField(default='[]')
    related = models.CharField(max_length=10)
    author = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)
    start = models.CharField(max_length=30)
    deadline = models.CharField(max_length=30)
    tags = models.TextField(default='[]')
    reminder = models.TextField(default='')
    status = models.CharField(max_length=10)
    key = models.CharField(max_length=10)
    creating_time = models.CharField(max_length=30)
    editing_time = models.CharField(max_length=30)
    responsible = models.TextField(default='[]')

    objects = models.Manager()

    # @property
    # def sub_tasks(self):
    #     return eval(str(self.__sub_tasks))
    #
    # @sub_tasks.setter
    # def sub_tasks(self, value):
    #     self.__sub_tasks = models.TextField(str(value))


class Plan(models.Model):
    author = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=30)
    reminder = models.TextField(default='')
    key = models.CharField(max_length=10)

    objects = models.Manager()


class Queue(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=10)
    owner = models.IntegerField(0)
    opened_tasks = models.TextField(default='[]')
    failed_tasks = models.TextField(default='[]')
    solved_tasks = models.TextField(default='[]')

    objects = models.Manager()
    # TODO: закончить модели


class User(models.Model):
    uid = models.IntegerField(0)
    nick = models.CharField(max_length=100)
    queues = models.TextField(default='[]')
    tasks_author = models.TextField(default='[]')
    tasks_responsible = models.TextField(default='[]')
    notifications = models.TextField(default='[]')
    new_messages = models.TextField(default='[]')
