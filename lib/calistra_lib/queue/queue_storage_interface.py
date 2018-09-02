"""
This module contains IQueueStorage - basic interface for all QueueStorage
 classes, using different methods of storing queues
"""


class IQueueStorage:
    """
    This class represent basic interface for classes realized
    queue storage logic
    """
    def __init__(self, queues):
        self.queues = queues

    def save_queues(self):
        """
        This method unload queue in database
        :return: None
        """
        raise NotImplementedError()

    def add_queue(self, name, key, owner):
        """
        This method append queue in list of queues
        :param name: queue name
        :param key: access key
        :param owner: author of queue
        :return: added queue
        """
        raise NotImplementedError()

    def remove_queue(self, queue):
        """
        This method remove queue from storage
        :param queue: queue for removing
        :return: None
        """
        raise NotImplementedError()

    def get_queue_by_key(self, key):
        """
        This method using for getting queue by key
        :param key: access key
        :return: queried queue
        """
        raise NotImplementedError()

    def get_queue_by_name(self, name):
        """
        This method using for getting queue by key
        :param name: queue name
        :return: queried queue
        """
        raise NotImplementedError()

    def get_user_default_queue(self, user):
        """
        This method using for getting default queue from storage for user
        :param user: user for getting queue
        :return: queried queue
        """
        raise NotImplementedError()
