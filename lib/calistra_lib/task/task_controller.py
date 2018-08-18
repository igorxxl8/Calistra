from datetime import datetime as dt
from .task import Task, TaskStatus
from .task_storage import TaskStorage
from .queue import Queue

try:
    from lib.calistra_lib.exceptions.task_exceptions import *
    from lib.calistra_lib.exceptions.access_exceptions import *
    from lib.calistra_lib.exceptions.queue_exceptions import *

except ImportError:
    from calistra_lib.exceptions.task_exceptions import *
    from calistra_lib.exceptions.access_exceptions import *
    from calistra_lib.exceptions.queue_exceptions import *

TIME_FORMAT = '%d.%m.%Y.%H:%M'

DEFAULT_QUEUE = 'default'
ANONYMOUS_QUEUE = '__anon__'
UNDEFINED = '?'
GUEST = 'guest'


def get_date(string):
    return dt.strptime(string, TIME_FORMAT)


class TaskController:
    EDITING_MESSAGE = ""

    def __init__(self, task_storage: TaskStorage):
        self.tasks_storage = task_storage

    @classmethod
    def attach_message(cls, message):
        cls.EDITING_MESSAGE = ''.join([cls.EDITING_MESSAGE, ' ', message])

    def add_queue(self, name, key, owner) -> Queue:
        queue = self.tasks_storage.add_queue(name, key, owner.nick)
        self.tasks_storage.save_tasks()
        return queue

    def edit_queue(self, key, new_name, editor) -> Queue:
        queue = self.tasks_storage.get_queue_by_key(key)

        if queue is None:
            raise QueueNotFoundError(' key - {}'.format(key))

        if queue.owner != editor.nick:
            raise AccessDeniedError(' you cannot edit this queue')

        if queue.name == DEFAULT_QUEUE:
            raise EditingQueueError('default queue "{}" immutable'.
                                    format(DEFAULT_QUEUE))

        if queue.name == ANONYMOUS_QUEUE:
            raise EditingQueueError('anonymous queue "{}" immutable'.
                                    format(ANONYMOUS_QUEUE))

        queue.name = new_name
        self.tasks_storage.save_tasks()
        return queue

    def del_queue(self, key, recursive, owner) -> Queue:
        queue = self.tasks_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueNotFoundError('key - {}.'.format(key))

        if queue.owner != owner.nick:
            raise AccessDeniedError(' you cannot delete this queue')

        if queue.name == ANONYMOUS_QUEUE:
            raise DeletingQueueError('you cannot remove anonymous queue {}!'.
                                     format(ANONYMOUS_QUEUE))

        if not recursive and (queue.opened or queue.solved or queue.failed):
            raise DeletingQueueError('queue with key "{}" isn\'t empty. '
                                     'Delete all queue tasks or '
                                     'delete queue recursively'.format(key))

        deleted_tasks = []
        all_tasks = queue.opened + queue.solved + queue.failed
        for task in all_tasks:
            deleted_tasks += self.del_task(owner, task.key, recursive)
        self.tasks_storage.remove_queue(queue)
        self.tasks_storage.save_tasks()
        queue.opened = deleted_tasks
        return queue

    def get_queue_by_key(self, key):
        return self.tasks_storage.get_queue_by_key(key)

    def get_queues_by_owner(self, owner) -> list:
        if owner.nick == GUEST:
            raise AccessDeniedError('please, log in system with existing '
                                    'account or add new')

        queues = []
        for key in owner.queues:
            queues.append(self.tasks_storage.get_queue_by_key(key))
        return queues

    def get_queue_tasks(self, q_key, owner):
        queue = self.tasks_storage.get_queue_by_key(q_key)
        if queue is None:
            raise QueueNotFoundError('key - {}'.format(q_key))

        if queue.owner != owner.nick:
            raise AccessDeniedError('you cannot see this queue')

        return queue.tasks

    def add_task(self, author, name, queue_key, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key, create_time):

        if queue_key == UNDEFINED:
            queue_key = author.uid

        if deadline == UNDEFINED:
            deadline = None

        if start == UNDEFINED:
            start = None

        if responsible == UNDEFINED:
            responsible = []

        if tags == UNDEFINED:
            tags = None

        if priority is None:
            priority = 0

        if progress is None:
            progress = 0

        if deadline:
            deadline_date = get_date(deadline)
            if deadline_date < dt.now():
                raise TaskDeadlineError('the deadline cannot be earlier '
                                        'than current time')

            if start and (deadline_date < get_date(start)):
                raise TaskDeadlineError('the deadline for a task cannot '
                                        'be earlier than its start')

        parent_task = self.tasks_storage.get_task_by_key(parent)
        if parent and parent_task is None:
            raise TaskNotFoundError('parent task key "{}"'.format(parent))

        queue = self.tasks_storage.get_queue_by_key(queue_key)
        if queue is None:
            raise QueueNotFoundError('key - {}'.format(queue_key))

        parent_queue = self.tasks_storage.get_queue_with_task(parent_task)
        if parent_task and queue is not parent_queue:
            raise SubTaskError('sub task and its parent cannot be located in '
                               'different queues')

        task = self.tasks_storage.add_task(
            author=author.nick, name=name, queue=queue, description=description,
            parent=parent, linked=linked, responsible=responsible,
            priority=priority, progress=progress, start=start,
            deadline=deadline, tags=tags, reminder=reminder, key=key,
            create_time=create_time)

        self.tasks_storage.save_tasks()
        return task

    def edit_task(self, task, editor, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status, edit_time):
        TaskController.EDITING_MESSAGE = ('User "{}" edit task "{}":'.
                                          format(editor.nick, task.name))
        task_queue = self.tasks_storage.get_queue_with_task(task)

        try:
            self.check_access(editor, task, responsible, name, description,
                              parent, linked, responsible, priority, start,
                              deadline, tags, reminder)
            self.edit_status(task, task_queue, status, editor)
            self.edit_progress(task, progress)
            self.edit_name(task, name)
            self.edit_description(task, description)
            self.edit_parent(task, task_queue, parent)
            self.edit_linked(task, linked)
            self.edit_priority(task, priority)
            self.edit_start(task, start, deadline)
            self.edit_deadline(task, deadline)
            self.edit_tags(task, tags)
            self.edit_reminder(task, reminder)
            self.edit_responsible(task, responsible)
        except AppError as e:
            raise AppError(e)

        task.edit_time = edit_time

        self.tasks_storage.save_tasks()
        return task

    def check_access(self, user, task, responsible, *args):
        nick = user.nick
        # TODO: разрешить редактировать только автору
        if (nick not in task.responsible and
                nick != task.author):
            raise AccessDeniedError('you cannot edit this task'.format(nick))

        if responsible:
            if responsible == UNDEFINED:
                responsible = []
            task.responsible = responsible

        if nick in task.responsible and nick != task.author:
            for arg in args:
                if arg:
                    raise AccessDeniedError('You can not edit task param '
                                            'besides status and progress')

    @staticmethod
    def edit_progress(task, progress):
        if progress is not None:
            task.progress = progress
            TaskController.attach_message('progress: {}'.format(progress))

    @staticmethod
    def edit_name(task, name):
        if name:
            task.name = name
            TaskController.attach_message('name: {}'.format(name))

    @staticmethod
    def edit_description(task, description):
        if description:
            task.description = description
            TaskController.attach_message('description: {}'.format(description))

    def edit_parent(self, task, task_queue, parent):
        if parent:
            parent_task = self.tasks_storage.get_task_by_key(parent)
            parent_queue = self.tasks_storage.get_queue_with_task(parent_task)

            if parent == UNDEFINED:
                task.parent = None

            elif parent_task is None:
                raise TaskNotFoundError('parent task key - {}'.format(parent))

            elif parent_task and task_queue is not parent_queue:
                raise SubTaskError('sub task and its parent cannot be located'
                                   ' in different queues')

            elif task.key == parent:
                raise SubTaskError('parent and subtask cannot be the same task')

            else:
                subtasks = self.tasks_storage.get_sub_tasks(task)
                for subtask in subtasks:
                    if parent == subtask.key:
                        raise SubTaskError('parent task cannot be one of '
                                           'sub tasks of this task')
                task.parent = parent
                TaskController.attach_message('parent {}'.format(parent))

    @staticmethod
    def edit_linked(task, linked):
        if linked:
            task.linked = linked
            TaskController.attach_message('linked: {}'.format(linked))

    @staticmethod
    def edit_priority(task, priority):
        if priority is not None:
            task.priority = priority
            TaskController.attach_message('priority: {}'.format(priority))

    @staticmethod
    def edit_responsible(task, responsible):
        if responsible:
            if responsible == UNDEFINED:
                responsible = []
            task.responsible = responsible
            TaskController.attach_message('responsible: {}'.format(responsible))

    @staticmethod
    def edit_start(task, start, deadline):
        if start:
            if start == UNDEFINED:
                task.start = None
            elif (task.deadline and get_date(task.deadline) < get_date(start)
                  and deadline and get_date(deadline) < get_date(start)):

                raise TaskDeadlineError('deadline for a task cannot'
                                        ' be earlier than its start')
            else:
                task.start = start
                TaskController.attach_message('start: {}'.format(start))

    @staticmethod
    def edit_reminder(task, reminder):
        if reminder:
            task.reminder = reminder
            TaskController.attach_message('reminder: {}'.format(reminder))

    @staticmethod
    def edit_tags(task, tags):
        if tags:
            if tags == UNDEFINED:
                task.tags = None
            else:
                task.tags = tags
                TaskController.attach_message('tags: {}'.format(task.tags))

    @staticmethod
    def edit_deadline(task, deadline):
        if deadline:
            if deadline == UNDEFINED:
                task.deadline = None
            elif get_date(deadline) < dt.now():
                raise TaskDeadlineError('deadline can not be earlier than now')
            elif task.start and get_date(deadline) < get_date(task.start):
                raise TaskDeadlineError(
                    'the deadline for a task cannot be earlier '
                    'than its start')
            else:
                task.deadline = deadline
                TaskController.attach_message('deadline: {}'.format(deadline))

    def edit_status(self, task: Task, queue, status, editor):
        if status:
            if status == TaskStatus.CLOSED:
                if editor.nick != task.author:
                    raise TaskStatusError('you cannot set status "closed".'
                                          ' It\'s author rights.')

                if task.status == TaskStatus.SOLVED:
                    self.close_task(queue, task)
                else:
                    raise TaskStatusError('cannot set status "closed". '
                                          'First of all task must be solved')

            task.status = status
            TaskController.attach_message('status: {}'.format(status))
            if status == TaskStatus.SOLVED:
                self.move_in_solved(queue, task)
            if status == TaskStatus.FAILED:
                self.move_in_failed(queue, task)
            if status == TaskStatus.OPENED:
                self.move_in_opened(queue, task)

    def close_task(self, queue: Queue, task: Task):
        self.tasks_storage.remove_solved_task(task, queue)
        # notify user

    def move_in_opened(self, queue: Queue, task: Task):
        if task in self.tasks_storage.opened_tasks:
            raise TaskStatusError('cannot set status "opened". '
                                  'Task already opened')

        if task in self.tasks_storage.failed_tasks:
            if task.deadline and get_date(task.deadline) < dt.now():
                raise TaskStatusError(
                    'cannot set status "opened". Task failed. First of all,'
                    ' change deadline and open task again')

            queue.failed.remove(task)
        if task in self.tasks_storage.solved_tasks:
            queue.solved.remove(task)
        queue.opened.append(task)

    def move_in_solved(self, queue: Queue, task: Task):
        if task in self.tasks_storage.solved_tasks:
            raise TaskStatusError('cannot set status "solved". '
                                  'Task already solved')

        if task in self.tasks_storage.failed_tasks:
            raise TaskStatusError('cannot set status "solved". '
                                  'Failed task cannot be solved. '
                                  'First of all, change deadline and'
                                  ' open task again')

        queue.opened.remove(task)
        queue.solved.append(task)
        # notify user

    def move_in_failed(self, queue: Queue, task: Task):
        if task in self.tasks_storage.failed_tasks:
            raise TaskStatusError('cannot set status "failed". '
                                  'Task already failed')

        if task in self.tasks_storage.solved_tasks:
            queue.solved.remove(task)

        elif task in self.tasks_storage.opened_tasks:
            queue.opened.remove(task)
        queue.failed.append(task)
        # notify user

    def del_task(self, owner, key, recursive):
        task = self.find_task(key=key)
        if task is None:
            raise TaskNotFoundError('key - {}'.format(key))

        if owner.nick != task.author:
            raise AccessDeniedError('you cannot delete this task.')

        sub_tasks = self.find_sub_tasks(task)
        if sub_tasks and recursive is False:
            raise DeletingTaskError('task has sub tasks. Delete all sub tasks'
                                    ' or delete task recursively')

        self.tasks_storage.remove_opened_task(task)
        all_deleted_tasks = [task]

        for sub_task in sub_tasks:
            deleted_sub_tasks = self.del_task(owner, sub_task.key, recursive)
            all_deleted_tasks += deleted_sub_tasks

        self.tasks_storage.save_tasks()
        return all_deleted_tasks

    def find_task(self, name=None, key=None):
        if key is None:
            if name is None:
                return None
            return self.tasks_storage.get_task_by_name(name)
        return self.tasks_storage.get_task_by_key(key)

    def find_sub_tasks(self, parent_task):
        return self.tasks_storage.get_sub_tasks(parent_task)

    def update_tasks(self):
        failed_tasks = []
        for task in self.tasks_storage.opened_tasks:
            if task.deadline and get_date(task.deadline) < dt.now():
                task.status = TaskStatus.FAILED
                queue = self.tasks_storage.get_queue_with_task(task)
                self.move_in_failed(queue, task)
                failed_tasks.append(task)
        return failed_tasks

    def check_reminders(self):
        # TODO: Проверка напоминаний
        for task in self.tasks_storage.opened_tasks:
            pass
