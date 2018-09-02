"""This module contains class JsonQueueStorage which store all users queue
 in json format"""


from calistra_lib.constants import Constants
from calistra_lib.queue.queue import Queue
from calistra_lib.storage.json_serializer import JsonDatabase
from calistra_lib.queue.queue_storage_interface import IQueueStorage


class JsonQueueStorage(IQueueStorage):
    """This class represent instance for store queues in json format"""
    def __init__(self, path_to_queue_file):
        self.queue_db = JsonDatabase(path_to_queue_file, cls_seq=[Queue])
        super().__init__(self.queue_db.load())

    def save_queues(self):
        """
        This method unload queue in json database
        :return: None
        """
        self.queue_db.unload(self.queues)

    def add_queue(self, queue):
        """
        This method append queue in list of queues
        :param queue for adding
        :return: added queue
        """
        self.queues.append(queue)

    def remove_queue(self, queue):
        """
        This method remove queue from storage
        :param queue: queue for removing
        :return: None
        """
        self.queues.remove(queue)

    def get_queue_by_key(self, key):
        """
        This method using for getting queue by key
        :param key: access key
        :return: queried queue
        """
        for queue in self.queues:  # type: Queue
            if key == queue.key:
                return queue

    def get_queue_by_name(self, name):
        """
        This method using for getting queue by key
        :param name: queue name
        :return: queried queue
        """
        for queue in self.queues:
            if name == queue.name:
                return queue

    def get_user_default_queue(self, user):
        """
        This method using for getting default queue from storage for user
        :param user: user for getting queue
        :return: queried queue
        """
        for queue in self.queues:
            if queue.owner == user.uid:
                if queue.name == Constants.DEFAULT_QUEUE:
                    return queue

