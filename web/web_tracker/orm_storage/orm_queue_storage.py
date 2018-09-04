from calistra_lib.queue.queue_storage_interface import IQueueStorage
from web_tracker.models import Queue
from django.shortcuts import get_object_or_404


class ORMQueueStorage(IQueueStorage):
    def __init__(self):
        super().__init__(Queue.objects.all())

    def save_queues(self):
        for queue in self.queues:
            queue.save()

    def add_queue(self, queue):
        self.queues.create(
            name=queue.name,
            key=queue.key,
            owner=queue.owner
        )

    def remove_queue(self, queue):
        self.queues.filter(key=queue.key).delete()

    def get_queue_by_key(self, key):
        try:
            return self.queues.get(key=key)
        except Exception:
            return None

    def find_queue(self, key=None, name=None, owner=None):
        queue = self.get_queue_by_key(key)
        if owner and queue is None:
            return self.get_user_default_queue(owner)
        if name and queue is None:
            return self.get_queue_by_name(name)
        return queue

    def get_queue_by_name(self, name):
        return self.queues.get(name=name)

    def get_user_default_queue(self, user):
        return self.queues.filter(owner=user.uid).get(name='default')
