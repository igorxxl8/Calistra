from calistra_lib.constants import Constants
from calistra_lib.queue.queue import Queue
from calistra_lib.storage.database import Database


class QueueStorage:
    def __init__(self, queue_db: Database):
        self.queue_db = queue_db
        self.queues = self.queue_db.load()

    def save_queues(self):
        self.queue_db.unload(self.queues)

    def add_queue(self, name, key, owner):
        self.queues.append(Queue(name, key, owner))
        return self.queues[-1]

    def remove_queue(self, queue):
        self.queues.remove(queue)

    def get_queue_by_key(self, key):
        for queue in self.queues:  # type: Queue
            if key == queue.key:
                return queue

    def get_queue_by_name(self, name):
        for queue in self.queues:
            if name == queue.name:
                return queue

    def get_user_default_queue(self, user):
        for queue in self.queues:
            if queue.owner == user.uid:
                if queue.name == Constants.DEFAULT_QUEUE:
                    return queue

