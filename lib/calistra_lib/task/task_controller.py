from datetime import datetime as dt
from .task import Task, TaskStatus
from .task_storage import TaskStorage
from queue.queue import Queue

try:
    from lib.calistra_lib.messages import Messages
    from lib.calistra_lib.exceptions.task_exceptions import *
    from lib.calistra_lib.exceptions.access_exceptions import *
    from lib.calistra_lib.exceptions.queue_exceptions import *

except ImportError:
    from calistra_lib.messages import Messages
    from calistra_lib.exceptions.task_exceptions import *
    from calistra_lib.exceptions.access_exceptions import *
    from calistra_lib.exceptions.queue_exceptions import *

TIME_FORMAT = '%d.%m.%Y.%H:%M'

DEFAULT_QUEUE = 'default'
UNDEFINED = '?'


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
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))

        if queue.owner != editor.nick:
            raise AccessDeniedError(Messages.CANNOT_EDIT_QUEUE)

        if queue.name == DEFAULT_QUEUE:
            raise EditingQueueError(Messages.DEFAULT_QUEUE_IMMUTABLE.
                                    format(DEFAULT_QUEUE))

        queue.name = new_name
        self.tasks_storage.save_tasks()
        return queue

    def del_queue(self, key, recursive, owner) -> Queue:
        queue = self.tasks_storage.get_queue_by_key(key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(key))

        if queue.owner != owner.nick:
            raise AccessDeniedError(Messages.CANNOT_DELETE_QUEUE)

        all_tasks = self.tasks_storage.get_all_queue_tasks(queue)
        if not recursive and all_tasks:
            raise DeletingQueueError(Messages.QUEUE_NOT_EMPTY.format(key))

        deleted_tasks = []
        all_tasks = self.tasks_storage.get_all_queue_tasks(queue)
        for task in all_tasks:
            deleted_tasks += self.del_task(owner, task.key, recursive)
        self.tasks_storage.remove_queue(queue)
        self.tasks_storage.save_tasks()
        queue.opened = deleted_tasks
        return queue

    def get_queue_by_key(self, key):
        return self.tasks_storage.get_queue_by_key(key)

    def get_queues_by_owner(self, owner) -> list:
        queues = []
        for key in owner.queues:
            queues.append(self.tasks_storage.get_queue_by_key(key))
        return queues

    def get_queue_tasks(self, q_key, owner):
        queue = self.tasks_storage.get_queue_by_key(q_key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(q_key))

        if queue.owner != owner.nick:
            raise AccessDeniedError(Messages.CANNOT_SEE_QUEUE)

        return queue.tasks

    def find_queues(self, key=None, name=None):
        if key is None and name is None:
            return []
        result = []
        if key:
            result = self.tasks_storage.get_queue_by_key(key)
        if name and not result:
            result = self.tasks_storage.get_queue_by_name(name)
        return result

    def add_task(self, author, name, queue_key, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key, creating_time):

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
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_NOW)

            if start and (deadline_date < get_date(start)):
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)

        parent_task = self.tasks_storage.get_task_by_key(parent)
        if parent and parent_task is None:
            raise TaskNotFoundError(Messages.SHOW_PARENT_KEY.format(parent))

        queue = self.tasks_storage.get_queue_by_key(queue_key)
        if queue is None:
            raise QueueNotFoundError(Messages.SHOW_KEY.format(queue_key))

        parent_queue = self.tasks_storage.get_queue_with_task(parent_task)
        if parent_task and queue is not parent_queue:
            raise SubTaskError(Messages.PARENT_IN_OTHER_QUEUE)

        task = self.tasks_storage.add_task(
            author=author.nick, name=name, queue=queue, description=description,
            parent=parent, linked=linked, responsible=responsible,
            priority=priority, progress=progress, start=start,
            deadline=deadline, tags=tags, reminder=reminder, key=key,
            creating_time=creating_time)

        self.tasks_storage.save_tasks()
        return task

    def edit_task(self, task, editor, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status, editing_time):

        TaskController.EDITING_MESSAGE = (Messages.USER_EDIT_TASK.
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
            raise e

        task.editing_time = editing_time

        self.tasks_storage.save_tasks()
        return task

    def check_access(self, user, task, responsible, *args):
        nick = user.nick
        if (nick not in task.responsible and
                nick != task.author):
            raise AccessDeniedError(Messages.CANNOT_EDIT_TASK)

        if task.key not in user.tasks_responsible and task.author != nick:
            raise AccessDeniedError(Messages.NEED_ACTIVATE_TASK)

        if nick in task.responsible and nick != task.author:
            for arg in args:
                if arg:
                    raise AccessDeniedError(Messages.CANNOT_EDIT_PARAM)

        if responsible:
            if responsible == UNDEFINED:
                responsible = []
            task.responsible = responsible

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
                raise TaskNotFoundError(Messages.SHOW_PARENT_KEY.format(parent))

            elif parent_task and task_queue is not parent_queue:
                raise SubTaskError(Messages.PARENT_IN_OTHER_QUEUE)

            elif task.key == parent:
                raise SubTaskError(Messages.PARENT_SAME_TASK)

            else:
                subtasks = self.tasks_storage.get_sub_tasks(task)
                for subtask in subtasks:
                    if parent == subtask.key:
                        raise SubTaskError(Messages.PARENT_IS_TASK_SUBTASK)
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

                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)
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
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_NOW)
            elif task.start and get_date(deadline) < get_date(task.start):
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)
            else:
                task.deadline = deadline
                TaskController.attach_message('deadline: {}'.format(deadline))

    def edit_status(self, task: Task, queue, status, editor):
        if status:
            if status == TaskStatus.CLOSED:
                if editor.nick != task.author:
                    raise TaskStatusError(Messages.CANNOT_SET_STATUS_CLOSED)

                if task.status == TaskStatus.SOLVED:
                    self.close_task(queue, task)
                else:
                    raise TaskStatusError(
                        Messages.CANNOT_SET_STATUS_CLOSED_FOR_UNSOLVED
                    )

            sub_tasks = self.find_sub_tasks(task)
            if status == TaskStatus.SOLVED:
                for sub_task in sub_tasks:
                    if sub_task.status != TaskStatus.SOLVED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_SOLVED_UNS_ST
                        )

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

    def activate_task(self, task):
        if task.status == TaskStatus.OPENED:
            task.status = TaskStatus.ACTIVATED
        self.tasks_storage.save_tasks()

    def move_in_opened(self, queue: Queue, task: Task):
        if task in self.tasks_storage.opened_tasks:
            raise TaskStatusError(Messages.TASK_ALREADY_SOLVED)

        if task in self.tasks_storage.failed_tasks:
            if task.deadline and get_date(task.deadline) < dt.now():
                raise TaskStatusError(
                    Messages.CANNOT_SET_STATUS_OPENED_FOR_FAILED
                )

            queue.failed_tasks.remove(task)
        if task in self.tasks_storage.solved_tasks:
            queue.solved_tasks.remove(task)
        queue.opened_tasks.append(task)

    def move_in_solved(self, queue: Queue, task: Task):
        if task in self.tasks_storage.solved_tasks:
            raise TaskStatusError(Messages.TASK_ALREADY_SOLVED)

        if task in self.tasks_storage.failed_tasks:
            raise TaskStatusError(Messages.CANNOT_SET_STATUS_SOLVED_FOR_FAILED)

        queue.opened_tasks.remove(task)
        queue.solved_tasks.append(task)
        # notify user

    def move_in_failed(self, queue: Queue, task: Task):
        if task in self.tasks_storage.failed_tasks:
            raise TaskStatusError(Messages.CANNOT_SET_STATUS_FAILED)

        if task in self.tasks_storage.solved_tasks:
            queue.solved_tasks.remove(task)

        elif task in self.tasks_storage.opened_tasks:
            queue.opened_tasks.remove(task)
        queue.failed_tasks.append(task)
        # notify user

    def del_task(self, owner, key, recursive):
        task = self.find_task(key=key)
        if task is None:
            raise TaskNotFoundError(Messages.SHOW_KEY.format(key))

        if owner.nick != task.author:
            raise AccessDeniedError(Messages.CANNOT_DELETE_TASK)

        sub_tasks = self.find_sub_tasks(task)
        if sub_tasks and recursive is False:
            raise DeletingTaskError(Messages.TASK_HAS_SUBTASKS)

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
