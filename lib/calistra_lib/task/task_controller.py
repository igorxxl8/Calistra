from datetime import datetime as dt
from .task import Task, TaskStatus
from .task_storage import TaskStorage

try:
    from lib.calistra_lib.constants import Constants
    from lib.calistra_lib.queue.queue import Queue
    from lib.calistra_lib.messages import Messages
    from lib.calistra_lib.exceptions.task_exceptions import *
    from lib.calistra_lib.exceptions.access_exceptions import *
    from lib.calistra_lib.exceptions.queue_exceptions import *

except ImportError:
    from calistra_lib.constants import Constants
    from calistra_lib.queue.queue import Queue
    from calistra_lib.messages import Messages
    from calistra_lib.exceptions.task_exceptions import *
    from calistra_lib.exceptions.access_exceptions import *
    from calistra_lib.exceptions.queue_exceptions import *


def get_date(string):
    return dt.strptime(string, Constants.TIME_FORMAT)


class TaskController:
    EDITING_MESSAGE = ""

    def __init__(self, task_storage: TaskStorage):
        self.tasks_storage = task_storage

    @classmethod
    def attach_message(cls, message):
        cls.EDITING_MESSAGE = ''.join([cls.EDITING_MESSAGE, ' ', message])

    def add_task(self, author, name, queue, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key, creating_time):

        if deadline == Constants.UNDEFINED:
            deadline = None

        if start == Constants.UNDEFINED:
            start = None

        if responsible == Constants.UNDEFINED:
            responsible = []

        if tags == Constants.UNDEFINED:
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

        if parent_task and parent_task.author != author.nick:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_TASK)

        if parent_task and queue.key != parent_task.queue:
            raise SubTaskError(Messages.PARENT_IN_OTHER_QUEUE)

        task = self.tasks_storage.add_task(
            author=author, name=name, start=start, queue=queue,
            description=description, parent=parent, progress=progress,
            tags=tags, responsible=responsible, priority=priority,
            linked=linked, deadline=deadline, key=key, reminder=reminder,
            creating_time=creating_time
        )
        if parent_task:
            self.link_task_with_sub_task(parent_task, task)
        self.tasks_storage.save_tasks()
        return task

    def edit_task(self, task, task_queue, editor, name, description, parent,
                  linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status, editing_time):

        TaskController.EDITING_MESSAGE = (Messages.USER_EDIT_TASK.
                                          format(editor.nick, task.name))

        try:
            self.check_access(editor, task, responsible, name, description,
                              parent, linked, responsible, priority, start,
                              deadline, tags, reminder)
            self.edit_status(task, status)
            self.edit_progress(task, progress)
            self.edit_name(task, name)
            self.edit_description(task, description)
            self.edit_linked(task, linked)
            self.edit_priority(task, priority)
            self.edit_start(task, start, deadline)
            self.edit_deadline(task, deadline)
            self.edit_tags(task, tags)
            self.edit_reminder(task, reminder)
            self.edit_responsible(task, responsible)
            self.edit_parent(task, task_queue, parent)
        except AppError as e:
            raise e

        task.editing_time = editing_time

        self.tasks_storage.save_tasks()
        return task

    def link_task_with_sub_task(self, parent_task: Task, sub_task: Task):
        parent_task.sub_tasks.append(sub_task.key)
        self.tasks_storage.save_tasks()

    def unlink_task_and_sub_task(self, parent_task: Task, sub_task: Task):
        for task_key in parent_task.sub_tasks:
            if task_key == sub_task.key:
                parent_task.sub_tasks.remove(task_key)
                break

        self.tasks_storage.save_tasks()

    @staticmethod
    def check_access(user, task, responsible, *args):
        nick = user.nick

        if task.key not in user.tasks_responsible and task.author != nick:
            raise AccessDeniedError(Messages.NEED_ACTIVATE_TASK)

        if nick in task.responsible and nick != task.author:
            for arg in args:
                if arg:
                    raise AccessDeniedError(Messages.CANNOT_EDIT_PARAM)

        if responsible:
            if responsible == Constants.UNDEFINED:
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
            if responsible == Constants.UNDEFINED:
                responsible = []
            task.responsible = responsible
            TaskController.attach_message('responsible: {}'.format(responsible))

    @staticmethod
    def edit_start(task, start, deadline):
        if start:
            if start == Constants.UNDEFINED:
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
            if tags == Constants.UNDEFINED:
                task.tags = None
            else:
                task.tags = tags
                TaskController.attach_message('tags: {}'.format(task.tags))

    @staticmethod
    def edit_deadline(task, deadline):
        if deadline:
            if deadline == Constants.UNDEFINED:
                task.deadline = None
            elif get_date(deadline) < dt.now():
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_NOW)
            elif task.start and get_date(deadline) < get_date(task.start):
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)
            else:
                task.deadline = deadline
                TaskController.attach_message('deadline: {}'.format(deadline))

    def edit_status(self, task: Task, status):
        if status:
            if status == task.status:
                raise TaskStatusError(
                    Messages.CANNOT_SET_SAME_STATUS.format(
                        status, task.name, status)
                )

            if status == TaskStatus.SOLVED:
                if task.status == TaskStatus.FAILED:
                    raise TaskStatusError(
                        Messages.CANNOT_SET_STATUS_SOLVED_FOR_FAILED)

                for sub_task in self.get_sub_tasks(task):
                    if sub_task.status != TaskStatus.SOLVED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_SOLVED_UNS_ST)

                    if sub_task.status == TaskStatus.FAILED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_SOLVED_FAILED_ST)

            if status == TaskStatus.OPENED:
                if task.status == TaskStatus.FAILED:
                    raise TaskStatusError(
                        Messages.CANNOT_SET_STATUS_OPENED_FOR_FAILED)
                for sub_task in self.get_sub_tasks(task):
                    if sub_task.status == TaskStatus.FAILED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_OPENED_FAILED_ST
                        )

            task.status = status
            TaskController.attach_message('status: {}'.format(status))

    def edit_parent(self, task, task_queue, parent):
        if parent:
            parent_task = self.tasks_storage.get_task_by_key(task.parent)
            new_parent_task = self.tasks_storage.get_task_by_key(parent)

            if parent == Constants.UNDEFINED:
                task.parent = None

            elif new_parent_task is None:
                raise TaskNotFoundError(Messages.SHOW_PARENT_KEY.format(parent))

            elif new_parent_task and task_queue.key != new_parent_task.queue:
                raise SubTaskError(Messages.PARENT_IN_OTHER_QUEUE)

            elif task.key == parent:
                raise SubTaskError(Messages.PARENT_SAME_TASK)

            else:
                for subtask in task.sub_tasks:
                    if parent == subtask:
                        raise SubTaskError(Messages.PARENT_IS_TASK_SUBTASK)
                if parent_task:
                    self.unlink_task_and_sub_task(parent_task, task)
                task.parent = parent
                self.link_task_with_sub_task(new_parent_task, task)
                TaskController.attach_message('parent {}'.format(parent))

    def activate_task(self, task):
        if task.status == TaskStatus.OPENED:
            task.status = TaskStatus.ACTIVATED
        self.tasks_storage.save_tasks()

    def remove_task(self, task: Task, remover, recursive):
        if remover.nick != task.author:
            raise AccessDeniedError(Messages.CANNOT_DELETE_TASK)

        sub_tasks = self.get_sub_tasks(task)
        if sub_tasks and recursive is False:
            raise DeletingTaskError(Messages.TASK_HAS_SUBTASKS)

        self.tasks_storage.remove_task(task)
        parent_task = self.tasks_storage.get_task_by_key(task.parent)
        if parent_task:
            self.unlink_task_and_sub_task(parent_task, task)
        all_deleted_tasks = [task]

        for sub_task in sub_tasks:
            deleted_sub_tasks = self.remove_task(sub_task, remover, recursive)
            all_deleted_tasks += deleted_sub_tasks

        self.tasks_storage.save_tasks()
        return all_deleted_tasks

    def get_task_by_key(self, key):
        task = self.tasks_storage.get_task_by_key(key)
        if task is None:
            raise TaskNotFoundError(Messages.SHOW_KEY.format(key))
        return task

    def find_task(self, name=None, key=None):
        if key is None:
            if name is None:
                return None
            return self.tasks_storage.get_task_by_name(name)
        return self.tasks_storage.get_task_by_key(key)

    def get_sub_tasks(self, parent_task):
        return self.tasks_storage.get_sub_tasks(parent_task)

    def update_tasks(self):
        # TODO: переделать метод
        failed_tasks = []
        for task in self.tasks_storage.tasks:
            if task.deadline and get_date(task.deadline) < dt.now():
                task.status = TaskStatus.FAILED
                queue = self.tasks_storage.get_queue_with_task(task)
                self.move_in_failed(queue, task)
                failed_tasks.append(task)
        return failed_tasks

    def check_reminders(self):
        # TODO: Проверка напоминаний
        # for task in self.tasks_storage.opened_tasks:
        pass
