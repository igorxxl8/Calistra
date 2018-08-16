from .task import Task
from .task_storage import TaskStorage
from .queue import Queue
from .task_exceptions import QueueError, TaskError
from datetime import datetime as dt

TIME_FORMAT = '%d.%m.%Y.%H:%M'

DEFAULT_QUEUE = 'default'
ANONYMOUS_QUEUE = '__anon__'


def get_date(string):
    return dt.strptime(string, TIME_FORMAT)


class TaskController:
    def __init__(self, task_storage: TaskStorage):
        self.tasks_storage = task_storage

    def add_queue(self, name, key, owner) -> Queue:
        queue = self.tasks_storage.add_queue(name, key, owner.nick)
        self.tasks_storage.save_tasks()
        return queue

    def edit_queue(self, key, new_name, editor) -> Queue:
        queue = self.tasks_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueError('Unable to edit: '
                             'Queue with key "{}" didn\'t found'.format(key))
        if queue.owner != editor.nick:
            raise QueueError('Access denied. You cannot edit this queue')

        if queue.name == DEFAULT_QUEUE:
            raise QueueError('It\'s unable to edit '
                             'default queue "{}"'.format(DEFAULT_QUEUE))

        if queue.name == ANONYMOUS_QUEUE:
            raise QueueError('It\'s unable to edit '
                             'anonymous queue "{}"'.format(ANONYMOUS_QUEUE))
        queue.name = new_name
        self.tasks_storage.save_tasks()
        return queue

    def del_queue(self, key, recursive, owner) -> Queue:
        queue = self.tasks_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueError('Queue with key "{}" didn\'t found.'.format(key))
        if queue.owner != owner.nick:
            raise QueueError('Access denied. You cannot delete this queue')
        if queue.name == ANONYMOUS_QUEUE:
            raise QueueError('Unable to delete queue "__anon__"!')
        if not recursive and queue.tasks:
            raise QueueError('Queue with key "{}" isn\'t empty. '
                             'Delete all queue tasks or '
                             'delete queue recursively'.format(key))

        deleted_tasks = []
        for task in queue.tasks:
            deleted_tasks += self.del_task(owner, task.key, recursive)
            deleted_tasks.append(task)
        self.tasks_storage.remove_queue(queue)
        self.tasks_storage.save_tasks()
        queue.tasks = deleted_tasks
        return queue

    def get_queues_by_owner(self, owner) -> list:
        if owner.nick == 'guest':
            raise QueueError('You cannot see queues. Please, sign in system')
        queues = []
        for key in owner.queues:
            queues.append(self.tasks_storage.get_queue_by_key(key))
        return queues

    def get_queue_tasks(self, q_key, owner):
        queue = self.tasks_storage.get_queue_by_key(q_key)
        if queue is None:
            raise QueueError('Unable to edit: '
                             'Queue with key "{}" didn\'t found'.format(q_key))
        if queue.owner != owner.nick:
            raise QueueError('Access denied. You cannot see this queue')

        return queue.tasks

    def add_task(self, author, name, queue_key, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):

        if queue_key == '?':
            queue_key = author.uid

        if deadline == '?':
            deadline = None

        if start == '?':
            start = None

        if responsible == '?':
            responsible = []

        if tags == '?':
            tags = None

        if deadline:
            deadline_date = get_date(deadline)
            if deadline_date < dt.now():
                raise TaskError('The deadline can not be earlier than now')
            if start and (deadline_date < get_date(start)):
                raise TaskError('The deadline for a task cannot be earlier '
                                'than its start')

        parent_task = self.tasks_storage.get_task_by_key(parent)
        if parent and parent_task is None:
            raise TaskError('Parent task with key "{}" '
                            'does not exist'.format(parent))

        queue = self.tasks_storage.get_queue_by_key(queue_key)
        if queue is None:
            raise TaskError('Queue "{}" did not found'.format(queue_key))

        parent_queue = self.tasks_storage.get_queue_with_task(parent_task)
        if parent_task and queue is not parent_queue:
            raise TaskError('The subtask and the main task cannot '
                            'be in different queues. For the subtask, '
                            'specify the queue that hosts the main task')

        task = self.tasks_storage.add_task(
            author=author.nick, name=name, queue=queue, description=description,
            parent=parent, linked=linked, responsible=responsible,
            priority=priority, progress=progress, start=start,
            deadline=deadline, tags=tags, reminder=reminder, key=key)

        self.tasks_storage.save_tasks()
        return task

    def edit_task(self, key, editor, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):

        task = self.find_task(key=key)
        if task is None:
            raise TaskError('Task with key "{}" didn\'t found'.format(key))

        online_user = editor.nick
        # TODO: разрешить редактировать только автору
        if (online_user not in task.responsible and
                online_user != task.author):
            raise TaskError('Access denied: You can not '
                            'edit this task'.format(online_user))

        if responsible:
            if responsible == '?':
                responsible = []
            task.responsible = responsible

        if (online_user in task.responsible and
                online_user != task.author and
                (name or description or parent or linked or responsible or
                 priority or start or deadline or tags or reminder)):
            raise TaskError('You can not edit task param '
                            'besides status and progress')

        if progress is not None:
            task.progress = progress

        if status:
            task.status = status

        if name:
            task.name = name

        if description:
            task.description = description

        if parent:
            parent_task = self.tasks_storage.get_task_by_key(parent)
            parent_queue = self.tasks_storage.get_queue_with_task(parent_task)
            task_queue = self.tasks_storage.get_queue_with_task(task)
            if parent == '?':
                task.parent = None
            elif parent_task is None:
                raise TaskError('Parent task with key "{}" '
                                'does not exist'.format(parent))

            elif parent_task and task_queue is not parent_queue:
                raise TaskError('The subtask and the main task cannot '
                                'be in different queues. For the subtask, '
                                'specify the queue that hosts the main task')

            elif task.key == parent:
                raise TaskError('The parent task cannot be the same task')
            else:
                subtasks = self.tasks_storage.get_subtasks(task)
                for subtask in subtasks:
                    if parent == subtask.key:
                        raise TaskError('The parent task cannot be one of '
                                        'the subtasks of this task')
                task.parent = parent

        if linked:
            task.linked = linked

        if priority is not None:
            task.priority = priority

        if start:
            if start == '?':
                task.start = None
            elif (task.deadline and get_date(task.deadline) < get_date(start)
                  and deadline and get_date(deadline) < get_date(start)):

                raise TaskError('The deadline for a task cannot be earlier '
                                'than its start')
            else:
                task.start = start

        if deadline:
            if deadline == '?':
                task.deadline = None
            elif deadline < dt.now():
                raise TaskError('The deadline can not be earlier than now')
            elif task.start and get_date(deadline) < get_date(task.start):
                raise TaskError('The deadline for a task cannot be earlier '
                                'than its start')
            else:
                task.deadline = deadline

        if tags:
            if tags == '?':
                task.tags = None
            else:
                task.tags = tags

        if reminder:
            task.reminder = reminder

        self.tasks_storage.save_tasks()
        return task

    def del_task(self, owner, key, recursive):
        task = self.find_task(key=key)
        if task is None:
            raise TaskError('Task with key "{}" didn\'t found'.format(key))
        if owner.nick != task.author:
            raise TaskError('Access denied. You cannot delete this task.')

        sub_tasks = self.tasks_storage.get_subtasks(task)
        if sub_tasks and recursive is False:
            raise TaskError('Can not delete task. It has subtasks. '
                            'Delete all subtasks or delete task recursively')

        all_deleted_tasks = []
        self.tasks_storage.remove_task(task)
        all_deleted_tasks.append(task)
        for sub_task in sub_tasks:
            deleted_sub_tasks = self.del_task(owner, sub_task.key, recursive)
            all_deleted_tasks += deleted_sub_tasks
        self.tasks_storage.save_tasks()
        # TODO: добавить уведомлении о удалении задачи ответственным
        return all_deleted_tasks

    def find_task(self, name=None, key=None):
        if key is None:
            if name is None:
                return None
            return self.tasks_storage.get_task_by_name(name)
        return self.tasks_storage.get_task_by_key(key)

    def find_sub_tasks(self, parent_task):
        return self.tasks_storage.get_subtasks(parent_task)
