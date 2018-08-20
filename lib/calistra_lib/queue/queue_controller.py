from .queue import Queue

try:
    from lib.calistra_lib.task.task import Task, TaskStatus
    from lib.calistra_lib.constants import Constants
    from lib.calistra_lib.messages import Messages
    from lib.calistra_lib.exceptions.access_exceptions import *
    from lib.calistra_lib.exceptions.queue_exceptions import *
    from lib.calistra_lib.queue.queue_storage import QueueStorage

except ImportError:
    from calistra_lib.task.task import Task, TaskStatus
    from calistra_lib.constants import Constants
    from calistra_lib.messages import Messages
    from calistra_lib.exceptions.queue_exceptions import *
    from calistra_lib.exceptions.access_exceptions import *
    from calistra_lib.queue.queue_storage import QueueStorage


class QueueController:
    def __init__(self, queue_storage: QueueStorage):
        self.queue_storage = queue_storage

    def add_queue(self, name, key, owner) -> Queue:
        queue = self.queue_storage.add_queue(name, key, owner.uid)
        self.queue_storage.save_queues()
        return queue

    def edit_queue(self, key, new_name, editor) -> Queue:
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
        return self.queue_storage.get_user_default_queue(user)

    def get_queue_by_key(self, key):
        queue = self.queue_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))
        return queue

    def get_user_queues(self, user) -> list:
        queues = []
        for queue_key in user.queues:
            queue = self.get_queue_by_key(queue_key)
            queues.append(queue)

        if not queues:
            raise QueueNotFoundError(Messages.QUEUES_NOT_FOUND)

        return queues

    def link_queue_with_task(self, queue, task):
        queue.opened_tasks.append(task.key)
        self.queue_storage.save_queues()

    def unlink_queue_and_task(self, queue, task):
        key = task.key
        if key in queue.opened_tasks:
            queue.opened_tasks.remove(key)
        elif key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        elif key in queue.failed_tasks:
            queue.failed_tasks.remove(key)
        self.queue_storage.save_queues()

    def move_in_opened(self, queue: Queue, task: Task):
        key = task.key
        if key in queue.failed_tasks:
            queue.failed_tasks.remove(key)
        if key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        queue.opened_tasks.append(key)
        self.queue_storage.save_queues()

    def move_in_solved(self, queue: Queue, task: Task):
        queue.opened_tasks.remove(task.key)
        queue.solved_tasks.append(task.key)
        self.queue_storage.save_queues()

    def move_in_failed(self, queue: Queue, task: Task):
        key = task.key
        if key in queue.solved_tasks:
            queue.solved_tasks.remove(key)
        elif key in queue.opened_tasks:
            queue.opened_tasks.remove(key)
        queue.failed_tasks.append(key)
        self.queue_storage.save_queues()
