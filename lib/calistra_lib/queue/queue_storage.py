"""This module contains class QueueStorage which store all users queue"""


from calistra_lib.constants import Constants
from calistra_lib.queue.queue import Queue
from calistra_lib.storage.database import Database


class QueueStorage:
    def __init__(self, queue_db: Database):
        self.queue_db = queue_db
        self.queues = self.queue_db.load()

    def save_queues(self):
        """

        :return: None
        """
        self.queue_db.unload(self.queues)

    def add_queue(self, name, key, owner):
        """
        This method append queue in list of queues
        :param name: queue name
        :param key: access key
        :param owner: author of queue
        :return: added queue
        """
        self.queues.append(Queue(name, key, owner))
        return self.queues[-1]

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

