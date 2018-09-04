"""This module contains class TaskController, which manipulate tasks entities"""


from datetime import datetime as dt

from .task import Task, TaskStatus, RelatedTaskType
from .task_storage_interface import ITaskStorage
from calistra_lib.task.reminder import Reminder
from calistra_lib.constants import Constants, Time
from calistra_lib.messages import Messages
from calistra_lib.exceptions.task_exceptions import *
from calistra_lib.exceptions.access_exceptions import *
from calistra_lib.exceptions.queue_exceptions import *


class TaskController:
    """
    This class define entity for work manipulate tasks and its params
    """
    EDITING_MESSAGE = ""

    def __init__(self, task_storage: ITaskStorage):
        self.tasks_storage = task_storage

    @classmethod
    def attach_message(cls, message):
        """
        This method appends a message about changing the task attributes
        :param: message
        :return None
        """
        cls.EDITING_MESSAGE = ''.join([cls.EDITING_MESSAGE, ' ', message])

    def connect_planed_task(self, task: Task):
        """
        This method using for adding task made by plan to tasks storage
        :param task:
        :return:
        """
        self.tasks_storage.add_task(task)
        self.tasks_storage.save_tasks()

    def add_task(self, author, name, queue, description=None, parent=None,
                 related=None, responsible=None, priority=None, progress=None,
                 start=None, deadline=None, tags=None, reminder=None, key=None,
                 creating_time=None):
        """
        This method created task entity and append it to other tasks
        :param author:
        :param name:
        :param queue:
        :param description:
        :param parent:
        :param related:
        :param responsible:
        :param priority:
        :param progress:
        :param start:
        :param deadline:
        :param tags:
        :param reminder:
        :param key:
        :param creating_time:
        :raises TaskNotFoundError, AccessDeniedError, SubTaskError
        :return: added task
        """

        parent_task = self.tasks_storage.get_task_by_key(parent)

        if parent and parent_task is None:
            raise TaskNotFoundError(Messages.SHOW_PARENT_KEY.format(parent))

        if parent_task and parent_task.author != author.nick:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_TASK)

        if parent_task and queue.key != parent_task.queue:
            raise SubTaskError(Messages.PARENT_IN_OTHER_QUEUE)

        task = Task(
            author=author.nick, name=name, start=start, queue=queue.key,
            description=description, parent=parent, progress=progress,
            tags=tags, responsible=responsible, priority=priority,
            related=related, deadline=deadline, key=key, reminder=reminder,
            creating_time=creating_time
        )
        self.tasks_storage.add_task(task)

        if parent_task:
            self.link_task_with_sub_task(parent_task, task)

        self.tasks_storage.save_tasks()
        return task

    def check_related_tasks(self, related, task_key):
        """
        This method check format of related tasks and they existence
        :param related: keys of associated tasks and its type in string format
        :param task_key: key of the task for which the associated task is set
        :raise RelatedTaskError
        :return: None
        """
        if related == Constants.UNDEFINED:
            return None

        link_attrs = related.split(':')

        task_keys = link_attrs[0].split(',')
        if link_attrs[1] == RelatedTaskType.CONTROLLER:
            if len(task_keys) != 1:
                raise RelatedTaskError(
                    Messages.CAN_BE_ONLY_ONE_CONTROLLER_TASK.format(
                        len(task_keys))
                )

        for key in task_keys:
            if key == task_key:
                raise RelatedTaskError(
                    Messages.TASK_CANNOT_BE_RELATED_TO_ITSELF.format(key))

            task = self.get_task_by_key(key)
            if (link_attrs[1] == RelatedTaskType.BLOCKER and
                    task.status == TaskStatus.SOLVED):
                raise RelatedTaskError(
                    Messages.CANNOT_USE_TASK_AS_BLOCKER.format(
                        task.name, task.key
                    )
                )

            if task.status == TaskStatus.SOLVED or task.status == TaskStatus.FAILED:
                raise RelatedTaskError(
                    Messages.CANNOT_LINK_TASK_WITH_SOLVED_TASK.format(
                        task.name, task.key)
                )

    def edit_task(self, task, task_queue, editor, name=None, description=None,
                  parent=None, related=None, responsible=None, priority=None,
                  progress=None, start=None, deadline=None, tags=None,
                  reminder=None, status=None, editing_time=None):
        """
        This method using for editing task and its attributes
        :param task: edited task
        :param task_queue: queue where task located
        :param editor: user who want to edit this task
        :param name: new task name
        :param description:
        :param parent:
        :param related:
        :param responsible:
        :param priority:
        :param progress:
        :param start:
        :param deadline:
        :param tags:
        :param reminder:
        :param status:
        :param editing_time: time when task was edited
        :raise AccessDeniedError, SubTaskError, TaskDeadlineError,
        TaskNotFoundError
        :return: edited task
        """

        TaskController.EDITING_MESSAGE = (
            Messages.USER_EDIT_TASK.format(editor.nick, task.name, task.key)
        )

        try:
            self.check_access(editor, task, responsible, name, description,
                              parent, related, responsible, priority, start,
                              deadline, tags, reminder)
            self.edit_start(task, start, deadline)
            self.edit_deadline(task, deadline)
            self.edit_related(task, related)
            self.edit_status(task, status)
            self.edit_progress(task, progress)
            self.edit_name(task, name)
            self.edit_description(task, description)
            self.edit_priority(task, priority)
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
        """
        This method add sub task key in list of sub tasks for defined task
        :param parent_task: task which has current sub task
        :param sub_task: sub task for linking
        :return: None
        """
        parent_task.sub_tasks.append(sub_task.key)
        self.tasks_storage.save_tasks()

    def unlink_task_and_sub_task(self, parent_task: Task, sub_task: Task):
        """
        This method delete sub task key from list of sub tasks for defined
         parent task
        :param parent_task:  task which has current sub task
        :param sub_task: sub task for unlinking
        :return: None
        """
        for task_key in parent_task.sub_tasks:
            if task_key == sub_task.key:
                parent_task.sub_tasks.remove(task_key)
                break

        self.tasks_storage.save_tasks()

    @staticmethod
    def check_access(user, task, responsible, *args):
        """
        This method using for check access of current user
        :param user: user who want to get access to task
        :param task: the task that the user wants to access
        :param responsible: new responsible users
        :param args: edited task attributes
        :raise AccessDeniedError
        :return: None
        """
        nick = user.nick

        # if user is not task responsible and author he cannot get access to
        # task
        if task.key not in user.tasks_responsible and task.author != nick:
            raise AccessDeniedError(Messages.NEED_ACTIVATE_TASK)

        # if responsible user try to change arguments which he cannot change
        # appear error
        if nick in task.responsible and nick != task.author:
            for arg in args:
                if arg:
                    raise AccessDeniedError(Messages.CANNOT_EDIT_PARAM)

        # if defined new responsible user we update task responsible
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
    def edit_related(task, related):
        if related:
            if related == Constants.UNDEFINED:
                task.related = None
            else:
                task.related = related

            TaskController.attach_message('Related: {}'.format(related))

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
        """
        This method check correctness of new start time and apply it
        :param task: edited task
        :param start: new start time
        :param deadline: new deadline time
        :return: None
        """
        if start:
            deadline_time = Time.get_date(task.deadline)
            start_time = Time.get_date(start)
            if start == Constants.UNDEFINED:
                task.start = None
            # when start deadline time bigger than deadline time or new
            # deadline time appear error
            elif (task.deadline and deadline_time < start_time
                  and deadline and Time.get_date(deadline) < start_time):

                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)
            else:
                task.start = start

            TaskController.attach_message('start: {}'.format(start))

    @staticmethod
    def edit_reminder(task, reminder):
        if reminder:
            if reminder == Constants.UNDEFINED:
                reminder = None
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
        """
        This method using for checking new deadline time correctness
        :param task: edited task
        :param deadline: new dealine time
        :return: None
        """
        if deadline:
            if deadline == Constants.UNDEFINED:
                task.deadline = None

            # if deadline time earlier than current time, appear error
            elif Time.get_date(deadline) < dt.now():
                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_NOW)
            # if deadline time earlier than start time, appear error
            elif (task.start and Time.get_date(deadline) <
                  Time.get_date(task.start)):

                raise TaskDeadlineError(Messages.DEADLINE_CANNOT_EARLIER_START)

            else:
                task.deadline = deadline

            TaskController.attach_message('deadline: {}'.format(deadline))

    def edit_status(self, task: Task, status):
        """
        This method using for editing task status and check that status
        changing does not contradict logic
        :param task: edited task
        :param status: new task status
        :return: None
        """
        if status:
            # for task which has controller task it's impossible to change
            # status
            if task.related and task.related.endswith(
                    RelatedTaskType.CONTROLLER):
                raise TaskStatusError(
                    Messages.CANNOT_CHANGE_RELATED_TASK_STATUS.format(

                      task.name, task.status))

            # it's not necessary to change status if it already has it
            if status == task.status:
                raise TaskStatusError(
                    Messages.CANNOT_SET_SAME_STATUS.format(
                        status, task.name, status)
                )

            if status == TaskStatus.SOLVED:
                # cannot set solved status for task which has unsolved blockers
                # task
                if self.is_task_has_unsolved_blockers(task):
                    raise TaskStatusError(
                        Messages.CANNOT_SOLVE_TASK_WITH_UNSOLVED_BLOCKERS
                    )
                if task.status == TaskStatus.FAILED:
                    raise TaskStatusError(
                        Messages.CANNOT_SET_STATUS_SOLVED_FOR_FAILED)

                # task cannot be solved if it has unsolved sub tasks
                for sub_task in self.get_sub_tasks(task):
                    if sub_task.status != TaskStatus.SOLVED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_SOLVED_UNS_ST)

                    if sub_task.status == TaskStatus.FAILED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_SOLVED_FAILED_ST)

            if status == TaskStatus.OPENED:
                # when user want to reopen task, this task checking for
                # deadline correctness
                if task.status == TaskStatus.FAILED:
                    if task.deadline and Time.get_date(task.deadline) < dt.now():
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_OPENED_FOR_FAILED)

                # when user want to reopen task, this task checking for open
                # sub tasks if it has failed sub tasks appear error
                for sub_task in self.get_sub_tasks(task):
                    if sub_task.status == TaskStatus.FAILED:
                        raise TaskStatusError(
                            Messages.CANNOT_SET_STATUS_OPENED_FAILED_ST
                        )

            task.status = status
            TaskController.attach_message('status: {}'.format(status))

    def edit_parent(self, task, task_queue, parent):
        """
        This method check correctness of editing parent task
        :param task: task for editing
        :param task_queue: queue where task located
        :param parent: new parent task
        :raise TaskNotFoundError, SubTaskError
        :return: None
        """
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
                # task cannot be one of it sub tasks
                for subtask in task.sub_tasks:
                    if parent == subtask:
                        raise SubTaskError(Messages.PARENT_IS_TASK_SUBTASK)
                if parent_task:
                    self.unlink_task_and_sub_task(parent_task, task)
                task.parent = parent
                self.link_task_with_sub_task(new_parent_task, task)

            TaskController.attach_message('parent {}'.format(parent))

    def activate_task(self, task):
        """
        This method change opened status on activated, when responsible user
         confirm participation in executing task
        :param task: task for activating
        :return: None
        """
        if task.status == TaskStatus.OPENED:
            task.status = TaskStatus.ACTIVATED
        self.tasks_storage.save_tasks()

    def remove_task(self, task: Task, remover, recursive=False):
        """
        This method delete task from storage
        :param task: task for removing
        :param remover: user who try to remove task
        :param recursive: flag for removing all sub tasks if neccessary
        :return: task and sub tasks if they exist
        """
        if remover.nick != task.author:
            raise AccessDeniedError(Messages.CANNOT_DELETE_TASK)

        sub_tasks = self.get_sub_tasks(task)
        # when task has sub tasks and removing without recursive flag appear
        #  erorr
        if task.sub_tasks and recursive is False:
            raise DeletingTaskError(Messages.TASK_HAS_SUBTASKS)

        self.tasks_storage.remove_task(task)
        # find parent task and delete link to removed task
        parent_task = self.tasks_storage.get_task_by_key(task.parent)
        if parent_task:
            self.unlink_task_and_sub_task(parent_task, task)
        all_deleted_tasks = [task]

        # recursively remove all sub tasks
        for sub_task in sub_tasks:
            deleted_sub_tasks = self.remove_task(sub_task, remover, recursive)
            all_deleted_tasks += deleted_sub_tasks

        self.tasks_storage.save_tasks()
        return all_deleted_tasks

    def get_task_by_key(self, key):
        """
        This method get task from storage by key
        :param key: access key
        :raise TaskNotFoundError
        :return: requested task
        """
        task = self.tasks_storage.get_task_by_key(key)
        if not task:
            raise TaskNotFoundError(Messages.SHOW_KEY.format(key))
        return task

    def find_task(self, key=None, name=None, tag=None):
        if key is None:
            if name is None and tag is None:
                return None
            if name:
                return self.tasks_storage.get_task_by_name(name)
            if tag:
                return self.tasks_storage.get_task_by_tag(tag)
        return self.tasks_storage.get_task_by_key(key)

    def get_sub_tasks(self, parent_task):
        return self.tasks_storage.get_sub_tasks(parent_task)

    # functions which working with task params and in depends of it change
    # status and notify users
    def check_terms_and_reminders(self, task, notified_tasks, failed_tasks):
        """
        This method for defined task check it deadline and reminders time
         if they come this task append to failed and to notified task
         respectively
        :param task: task for checking terms and reminders
        :param notified_tasks: list of tasks for notify their responsible
        :param failed_tasks: list of failed tasks
        :return: None
        """
        if task.status != TaskStatus.FAILED:
            self.check_task_reminders(task, notified_tasks)
            self.check_task_deadline(task, failed_tasks)

    @staticmethod
    def check_task_deadline(task, failed_tasks):
        """
        This method for task check it deadline and if the deadline has passed
        (current time more than deadline time), append task to failed
        :param task: task for checking deadline
        :param failed_tasks: list of failed tasks
        :return: None
        """
        now = dt.now()
        if task.deadline:
            deadline_time = Time.get_date(task.deadline)
            if deadline_time < now:
                task.status = TaskStatus.FAILED
                failed_tasks.append(task)

    @staticmethod
    def check_task_reminders(task, notified_tasks):
        """
        This method for task check it reminder and if the time of notification
         user has come append it to other task for notification
        :param task:task for checking reminders
        :param notified_tasks: list of tasks for which need to notify users
        :return:None
        """
        messages = Reminder.check_auto_reminder(task)
        if messages:
            notified_tasks.append(Reminder.Reminder(task=task, messages=messages))

        if task.reminder:
            messages = Reminder.check_reminder_time(task)
            if messages:
                notified_tasks.append(Reminder.Reminder(task=task, messages=messages))

    def update_all(self):
        """
        This method checks each task if it needs update their status, track
         controllers and blockers for changing status, and check reminders for
          task for notification users

        :return: controllers, blockers, failed_tasks, notified_tasks
                controllers - tasks which has changed status and have depend
                tasks, for this depend task it's necessary to set equal status
                blockers - tasks which has blockers
                failed_tasks - tasks which were fail because it deadline has
                passed
                notified_tasks - tasks which triggered the notification of
                 users
        """
        controllers = []
        blockers = []
        failed_tasks = []
        notified_tasks = []
        for task in self.tasks_storage.tasks:
            self.update_related_tasks(task, controllers, blockers)
            self.check_terms_and_reminders(task, notified_tasks, failed_tasks)

        self.tasks_storage.save_tasks()
        return controllers, blockers, failed_tasks, notified_tasks

    def update_related_tasks(self, task, controllers, blockers):
        """
        This method check for task it related tasks an
        :param task: task which can has related tasks
        :param controllers: list of tasks-controllers
        :param blockers: list of tasks-blockers
        :return: None
        """
        if task.related:
            # get list of related task attr, where link_attrs[0] - keys of
            # related tasks, link_attr[1] - type of related task
            link_attrs = task.related.split(':')
            task_keys = link_attrs[0].split(',')
            # for controllers check it status and if it changed, change status
            # of current task
            if link_attrs[1] == RelatedTaskType.CONTROLLER:
                self.update_related_controller(task, task_keys[0],
                                               controllers)

            # for blockers check status if it solve and all blockers were solve,
            # notified user that curent task can be solved
            elif link_attrs[1] == RelatedTaskType.BLOCKER:
                if self.is_task_has_unsolved_blockers(task) is False:
                    if task.status != TaskStatus.SOLVED:
                        blockers.append(task)

    def update_related_controller(self, task, related_task_key, controllers):
        """
        This method for controller task check it status and if it changed,
        change status of task which has this controller
        :param task: task which has controller
        :param related_task_key: key of controller task
        :param controllers: list of tasks-controllers with change status
        :raise AppError
        :return: None
        """
        try:
            related_task = self.get_task_by_key(related_task_key)
            if related_task.status != task.status:
                task.status = related_task.status
                controllers.append(task)
        except AppError:
            task.related = None

    def is_task_has_unsolved_blockers(self, task):
        """
        This method  check task blockers and if they unsolved it return True
        else False
        :param task: task which can blockers
        :return: True - if has unsolved blockers
                False - if all blockers solved
        """
        # flag that using for define if task blocker solved
        flag = False
        if task.related is None:
            return False
        # get list of related task attr, where link_attrs[0] - keys of
        # related tasks, link_attr[1] - type of related task
        link_attrs = task.related.split(':')
        task_keys = link_attrs[0].split(',')
        for key in task_keys[:]:
            # skip current task
            if task.key == key:
                continue
            try:
                # try to find task in storage
                related_task = self.get_task_by_key(key)
                if related_task.status != TaskStatus.SOLVED:
                    flag = True
            except AppError:
                # if task in storage not found remove it key from related
                task_keys.remove(key)

        # update related tasks if they change. When task related blocker
        # deleted, his key will be deleted from task related record
        new_task_keys = ','.join(task_keys)
        new_related = new_task_keys
        if new_related:
            new_related = ':'.join([new_related, link_attrs[1]])
        # if all blockers were deleted related tasks reset
        if new_related == "":
            new_related = None
        task.related = new_related

        return flag
