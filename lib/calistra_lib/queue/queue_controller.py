"""This module contains class QueueController, whick using for working
with plans
"""


from .queue import Queue
from calistra_lib.task.task import Task
from calistra_lib.constants import Constants
from calistra_lib.messages import Messages
from calistra_lib.exceptions.queue_exceptions import *
from calistra_lib.exceptions.access_exceptions import *
from calistra_lib.queue.json_queue_storage import JsonQueueStorage


class QueueController:
    """This class represent methods for work with queue entity"""
    def __init__(self, queue_storage: JsonQueueStorage):
        self.queue_storage = queue_storage

    def add_queue(self, name, key, owner) -> Queue:
        """
        This method using for creating new queue
        :param name: queue name
        :param key: queue access key
        :param owner: user who create queue
        :return: added queue
        """
        queue = self.queue_storage.add_queue(name, key, owner.uid)
        self.queue_storage.save_queues()
        return queue

    def edit_queue(self, key, new_name, editor) -> Queue:
        """
        This method using for editing existing queue
        :param key: access key
        :param new_name: queue new name
        :param editor: user who now edit queue
        :return: edited queue
        """
        queue = self.queue_storage.get_queue_by_key(key)

        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))

        if queue.owner != editor.uid:
            raise AccessDeniedError(Messages.CANNOT_EDIT_QUEUE)

        if queue.name == Constants.DEFAULT_QUEUE:
            raise EditingQueueError(Messages.DEFAULT_QUEUE_IMMUTABLE.
                                    format(Constants.DEFAULT_QUEUE))

        queue.name = new_name
        self.queue_storage.save_queues()
        return queue

    def remove_queue(self, key, recursive, owner) -> Queue:
        """
        This method using for removing queue entity from storage
        :param key: access key
        :param recursive: flag which mean, confirm operation for nested tasks
        :param owner: user who create queue
        :return: deleted queue
        """
        queue = self.queue_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))

        if queue.name == Constants.DEFAULT_QUEUE:
            raise DeletingQueueError(Messages.DEFAULT_QUEUE_UNREMOVABLE)

        if queue.owner != owner.uid:
            raise AccessDeniedError(Messages.CANNOT_DELETE_QUEUE)

        if not recursive:
            if queue.opened_tasks or queue.solved_tasks or queue.failed_tasks:
                raise DeletingQueueError(Messages.QUEUE_NOT_EMPTY.format(key))

        self.queue_storage.remove_queue(queue)
        self.queue_storage.save_queues()
        return queue

    def get_user_default_queue(self, user):
        """
        This method using for get user default queue
        :param user: for this user perform getting queue
        :return: default queue
        """
        return self.queue_storage.get_user_default_queue(user)

    def get_queue_by_key(self, key):
        """
        This method using for get queue from queue storage by key
        :param key: access key
        :return: queried queue
        """
        queue = self.queue_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))
        return queue

    def get_user_queues(self, user) -> list:
        """
        This method using for getting all queue which create specified user
        :param user:
        :return: queried queue
        """
        queues = []
        for queue_key in user.queues:
            queue = self.get_queue_by_key(queue_key)
            queues.append(queue)

        if not queues:
            raise QueueNotFoundError(Messages.QUEUES_NOT_FOUND)

        return queues

    def link_queue_with_task(self, queue, task):
        """
        This method create link between task and queue
        :param queue: queue for linking
        :param task: task for linking
        :return: None
        """
        queue.opened_tasks.append(task.key)
        self.queue_storage.save_queues()

    def unlink_queue_and_task(self, queue, task):
        """
        This method delete link between queue and task
        :param queue: queue for unlinking
        :param task: task for unlinking
        :return: None
        """
        key = task.key
        if key in queue.opened_tasks:
            queue.opened_tasks.remove(key)
        elif key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        elif key in queue.failed_tasks:
            queue.failed_tasks.remove(key)
        self.queue_storage.save_queues()

    def move_in_opened(self, queue: Queue, task: Task):
        """
        This method move task to opened tasks in queue
        :param queue: queue which store task
        :param task: task for moving
        :return: None
        """
        key = task.key
        if key in queue.failed_tasks:
            queue.failed_tasks.remove(key)
        if key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        queue.opened_tasks.append(key)
        self.queue_storage.save_queues()

    def move_in_solved(self, queue: Queue, task: Task):
        """
        This method move task to solved tasks in queue
        :param queue: queue which store task
        :param task: task for moving
        :return: None
        """
        queue.opened_tasks.remove(task.key)
        queue.solved_tasks.append(task.key)
        self.queue_storage.save_queues()

    def move_in_failed(self, queue: Queue, task: Task):
        """
        This method move task to failed tasks in queue
        :param queue: queue which store task
        :param task: task for moving
        :return: None
        """
        key = task.key
        if key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        elif key in queue.opened_tasks:
            queue.opened_tasks.remove(key)
        queue.failed_tasks.append(key)
        self.queue_storage.save_queues()
