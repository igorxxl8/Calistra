"""This module contains class TaskStorage which store all tasks entities"""

from .task import Task
from calistra_lib.storage.database import Database


class TaskStorage:
    """
    This class using for store all tasks in one place
    """
    def __init__(self, tasks_db: Database):
        self.tasks_db = tasks_db
        self.tasks = self.tasks_db.load()

    def add_task(self, task):
        """This method append task to tasks list
        :param: task: task for adding
        :return: None
        """
        self.tasks.append(task)

    def remove_task(self, task):
        """
        This method using for deleting task from task storage
        :param task: task for removing
        :return: None
        """
        self.tasks.remove(task)

    def get_sub_tasks(self, task: Task):
        """
        This method using for getting task sub tasks
        :param task: parent task which has sub tasks
        :return: sub tasks
        """
        sub_tasks = []
        for sub_task_key in task.sub_tasks:
            sub_task = self.get_task_by_key(sub_task_key)
            sub_tasks.append(sub_task)
        return sub_tasks

    def get_task_by_key(self, key):
        """
        This method using for getting task by key from task storage
        :param key: access key
        :return: queried task
        """
        for task in self.tasks:
            if task.key == key:
                return task

    def get_task_by_name(self, name):
        """
        This method using for getting task by name from task storage
        :param name: task name
        :return: queried task
        """
        tasks = []
        for task in self.tasks:
            if task.name == name or task.name.startswith(name):
                tasks.append(task)
        return tasks

    def save_tasks(self):
        """
        This method using for save task in database
        :return: None
        """
        self.tasks_db.unload(self.tasks)
