"""This module contains basic task storage interface - ITaskStorage"""


class ITaskStorage:
    """This class represent basic interface for all classes implemented
    task storage instance
    """
    def __init__(self, tasks):
        self.tasks = tasks

    def add_task(self, task):
        """This method append task to tasks list
        :param: task: task for adding
        :return: None
        """
        raise NotImplementedError()

    def remove_task(self, task):
        """
        This method using for deleting task from task storage
        :param task: task for removing
        :return: None
        """
        raise NotImplementedError()

    def get_sub_tasks(self, task):
        """
        This method using for getting task sub tasks
        :param task: parent task which has sub tasks
        :return: sub tasks
        """
        raise NotImplementedError()

    def get_task_by_key(self, key):
        """
        This method using for getting task by key from task storage
        :param key: access key
        :return: queried task
        """
        raise NotImplementedError()

    def get_task_by_name(self, name):
        """
        This method using for getting task by name from task storage
        :param name: task name
        :return: queried task
        """
        raise NotImplementedError()

    def get_task_by_tag(self, tag):
        """
        This method using for getting task by tag from task storage
        :param tag: task tag
        :return: queried task
        """
        raise NotImplementedError()

    def save_tasks(self):
        """
        This method using for save task in database
        :return: None
        """
        raise NotImplementedError()