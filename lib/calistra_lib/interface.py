"""This module contains class Interface which manipulate all entities
in library
"""


from datetime import datetime as dt
from calistra_lib.constants import Constants, Time
from calistra_lib.messages import Messages
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.task.task import TaskStatus
from calistra_lib.task.task_controller import TaskController
from calistra_lib.exceptions.base_exception import AppError
from calistra_lib.user.user_controller import UserController
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.exceptions.access_exceptions import AccessDeniedError
from calistra_lib.exceptions.task_exceptions import (
    TaskNotFoundError,
    ActivationTaskError
)
from calistra_lib.exceptions.queue_exceptions import (
    AddingQueueError
)
from calistra_lib.logger import log


class Interface:
    """
    This class as facade combines functionality of task, queue, plan and user
     controllers, for convenient using
    """
    def __init__(self, online_user, queue_controller: QueueController,
                 user_controller: UserController, task_controller: TaskController,
                 plan_controller: PlanController):

        self.queue_controller = queue_controller
        self.task_controller = task_controller
        self.plan_controller = plan_controller
        self.user_controller = user_controller
        self.online_user = self.user_controller.find_user(nick=online_user)

    # functions for work with user instance
    @log
    def get_online_user(self):
        """
        This method using for getting current online object
        :raise: AccessDeniedError
        :return: online user
        """
        if self.online_user is None:
            raise AccessDeniedError(Messages.SIGN_IN)
        return self.online_user

    @log
    def set_online_user(self, user_nick):
        """
        This method using for setting current online user
        :param user_nick: nick of user
        :return: None
        """
        self.online_user = self.user_controller.find_user(nick=user_nick)

    @log
    def add_user(self, nick, uid, queue_key):
        """
        This method using for creating new user
        :param nick: user nick
        :param uid: user uid
        :param queue_key: key of default queue
        :return: added user
        """
        user = self.user_controller.add_user(nick, uid)
        self.add_queue(Constants.DEFAULT_QUEUE, queue_key, user)
        return user

    @log
    def clear_notifications(self, quantity=None):
        """
        This method using for delete user notifications
        :param quantity: quantity of deleting messages
        :raise ValueError
        :return: None
        """
        try:
            self.user_controller.clear_user_notifications(
                self.online_user, quantity)
        except ValueError as e:
            raise ValueError(e)

    @log
    def clear_new_messages(self, user=None):
        """
        This method clear new messages and transfer it in notifications storage
        :param user: user which new message will be deleted
        :return: None
        """
        if user is None:
            user = self.online_user
        self.user_controller.clear_new_messages(user)

    @log
    def update_all(self):
        """
        This method verifies and updated deadlines and plans tasks and notify
         user about in changing
        :return: None
        """
        # getting all entities which could changing
        # tasks which were creating by plans
        planed_tasks = self.plan_controller.update_all_plans()

        # controllers, blockers, failed tasks, task which produce notifications
        ctrls, blcks, failed, notified = self.task_controller.update_all()

        for task in planed_tasks:
            user = self.user_controller.find_user(nick=task.author)
            queue = self.queue_controller.get_user_default_queue(user)
            self.task_controller.connect_planed_task(task)
            self.queue_controller.link_queue_with_task(queue, task)
            self.user_controller.link_author_with_task(user, task)
            self.send_message_to_users(
                [user],
                Messages.PLANNED_TASK_WAS_ACTIVATED.format(task.name, task.key)
            )

        for task, messages in notified:
            users = self.find_users_by_name_list(
                task.responsible + [task.author])
            for message in messages:
                self.send_message_to_users(users, message, False)

        for task in failed:
            queue = self.queue_controller.get_queue_by_key(task.queue)
            self.queue_controller.move_in_failed(queue, task)
            users = self.find_users_by_name_list(
                task.responsible + [task.author])

            self.send_message_to_users(
                users, Messages.TASK_WAS_FAILED_DEADLINE_PASSED.format(
                    task.name, task.key, task.deadline)
            )

        for task in ctrls:
            users = self.find_users_by_name_list(
                task.responsible + [task.author])
            self.send_message_to_users(
                users,
                Messages.TASK_WAS_UPDATED_BY_CONTROLLER.format(
                    task.name, task.status)
            )

        for task in blcks:
            users = self.find_users_by_name_list(
                task.responsible + [task.author])
            self.send_message_to_users(
                users,
                Messages.TASK_BLOCKERS_WERE_SOLVED.format(task.name)
            )

    @log
    def send_message_to_users(self, users, message, show_time=True):
        """
        This method using for sending message and notifications to users
        :param users: notified users
        :param message: message which users get
        :param show_time: flag, which defines necessary to show time in
        notification
        :return: None
        """
        for user in users:
            self.user_controller.notify_user(user, message, show_time)

    # functions for work with queue instance
    def add_queue(self, name, key, owner=None):
        """
        This method using for creating queue
        :param name: name of queue
        :param key: access key
        :param owner: queue owner
        :return: added queue
        :raise: AppError
        """
        if owner is None:
            owner = self.get_online_user()
            if name == Constants.DEFAULT_QUEUE:
                raise AddingQueueError(Messages.CANNOT_NAME_AS_DEFAULT_QUEUE)

        try:
            queue = self.queue_controller.add_queue(name, key, owner)
        except AppError as e:
            raise e
        else:
            self.user_controller.link_user_with_queue(owner, queue)
            return queue

    @log
    def edit_queue(self, key, new_name):
        """
        This method using for editing queue
        :param key: access key
        :param new_name: new queue name
        :return: edited queue
        :raise: AppError
        """
        editor = self.get_online_user()
        try:
            return self.queue_controller.edit_queue(key, new_name, editor)
        except AppError as e:
            raise e

    @log
    def remove_queue(self, key, recursive):
        """
        This method using for removing queue
        :param key: access key
        :param recursive: flag, which mean that this operation repeated
         for tasks inside queue
        :return: removed queue
        """
        user = self.get_online_user()
        try:
            queue = self.queue_controller.remove_queue(key, recursive, user)
        except AppError as e:
            raise e

        self.user_controller.unlink_user_and_queue(user, queue)
        task_keys = queue.opened_tasks + queue.failed_tasks + queue.solved_tasks
        for task_key in task_keys:
            try:
                self.remove_task(task_key, recursive, True)
            except AppError:
                pass

        return queue

    @log
    def get_user_queues(self):
        """
        This method using for getting online user queues
        :return: queues
        """
        try:
            user = self.get_online_user()
            queues = self.queue_controller.get_user_queues(user)
        except AppError as e:
            raise e
        return queues

    @log
    def get_queue(self, queue_key, owner=None):
        """
        This method using for getting queue by key
        :param queue_key: access key
        :param owner: author of queue
        :return: queried queue
        """
        if owner is None:
            owner = self.online_user
        if queue_key == Constants.UNDEFINED:
            queue = self.queue_controller.get_user_default_queue(owner)
        else:
            queue = self.queue_controller.get_queue_by_key(queue_key)
        if queue.owner != owner.uid:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_QUEUE)
        return queue

    @log
    def find_queues(self, name):
        """
        This method using for getting queues by key
        :param name: queue name
        :return: result - queue which approach  by queue name
        """
        user = self.get_online_user()
        queues = self.queue_controller.get_user_queues(user)
        result = []
        for queue in queues:
            if queue.name == name or queue.name.startswith(name):
                result.append(queue)
        return result

    # functions for work with task instance
    @log
    def create_task(self, name, queue_key, description, parent, related,
                    responsible, priority, progress, start, deadline, tags,
                    reminder, key):
        """
        This method create task by rules
        :param name: task name
        :param queue_key:
        :param description:
        :param parent: key of parent task
        :param related: keys of related tasks
        :param responsible: user who can solve task
        :param priority: task priority
        :param progress: task progress
        :param start:
        :param deadline:
        :param tags:
        :param reminder:
        :param key: task key
        :raise AppError
        :return: created task
        """

        creating_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)
        author = self.get_online_user()
        queue = self.get_queue(queue_key, author)

        if related:
            self.task_controller.check_related_tasks(related, key)

        try:
            responsible_users = self.find_users_by_name_list(responsible)

            task = self.task_controller.add_task(
                author=author, name=name, queue=queue,
                description=description, parent=parent, related=related,
                responsible=responsible, priority=priority, progress=progress,
                start=start, deadline=deadline, tags=tags, reminder=reminder,
                key=key, creating_time=creating_time
            )
        except AppError as e:
            raise e

        for user in responsible_users:
            if user.uid == author.uid:
                self.user_controller.link_responsible_with_task(user, task)
            else:
                message = Messages.YOU_ASSIGNED.format(author.nick, task.name,
                                                       task.key, task.key)

                self.user_controller.notify_user(user, message)

        self.user_controller.link_author_with_task(author, task)
        self.queue_controller.link_queue_with_task(queue, task)

        return task

    @log
    def edit_task(self, key, name, description, parent, related,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):
        """
        This method using for editing task
        :param key:
        :param name:
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
        :raise: AppError
        :return: edited task
        """

        editing_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)
        editor = self.get_online_user()

        if related:
            self.task_controller.check_related_tasks(related, key)

        try:
            task = self.get_task(key)
            task_queue = self.queue_controller.get_queue_by_key(task.queue)

            if responsible is None:
                current_responsible = []
                new_responsible = []
            else:
                current_responsible = self.find_users_by_name_list(
                    task.responsible)
                new_responsible = self.find_users_by_name_list(responsible)

            task = self.task_controller.edit_task(
                task_queue=task_queue, task=task, editor=editor, name=name,
                description=description, parent=parent, related=related,
                priority=priority, progress=progress, start=start,
                deadline=deadline, tags=tags, reminder=reminder, status=status,
                responsible=responsible, editing_time=editing_time
            )

        except AppError as e:
            raise e

        else:
            dismissed_users, invited_users = self.get_responsible_diff(
                new_responsible, current_responsible)
            new_responsible = self.find_users_by_name_list(invited_users)
            dismissed_responsible = self.find_users_by_name_list(
                dismissed_users)

            for user in dismissed_responsible:
                self.user_controller.unlink_responsible_and_task(user, task)
                message = (Messages.YOU_SUSPENDED.format(task.name))
                self.user_controller.notify_user(user, message)

            for user in new_responsible:
                if user.uid == editor.uid:
                    self.user_controller.link_responsible_with_task(user, task)

                message = (Messages.YOU_ASSIGNED.format(editor.nick, task.name,
                                                        task.key, task.key))
                self.user_controller.notify_user(user, message)

            if task.author not in task.responsible:
                users = self.find_users_by_name_list(
                    task.responsible + [task.author])
            else:
                users = self.find_users_by_name_list(task.responsible)

            self.send_message_to_users(users,
                                       TaskController.EDITING_MESSAGE)

            if status is None:
                return task

            if task.status == TaskStatus.SOLVED:
                self.queue_controller.move_in_solved(task_queue, task)
                self.send_message_to_users(
                    users, Messages.TASK_SOLVED.format(task.name, editor.nick))

            elif task.status == TaskStatus.OPENED:
                self.queue_controller.move_in_opened(task_queue, task)
                self.send_message_to_users(
                    users,
                    Messages.TASK_REOPENED.format(task.name, editor.nick))

            elif task.status == TaskStatus.FAILED:
                self.queue_controller.move_in_failed(task_queue, task)
                self.send_message_to_users(
                    users, Messages.TASK_WAS_FAILED.format(task.name))

            return task

    @log
    def get_task(self, key, owner=None):
        """
        This method using for getting task by key
        :param key: access key
        :param owner: task owner
        :raise AccessDeniedError
        :return: queried task
        """
        if owner is None:
            owner = self.get_online_user()
        task = self.task_controller.get_task_by_key(key)
        if task.author != owner.nick and owner.nick not in task.responsible:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_TASK)
        return task

    @log
    def find_task(self, key=None, name=None):
        """
        This method using for getting task by key or by name
        :param key: access key
        :param name: access name
        :raise TaskNotFoundError, AccessDeniedError
        :return: tasks which approach request
        """
        user = self.get_online_user()
        tasks = self.task_controller.find_task(key=key, name=name)

        if tasks is None:
            raise TaskNotFoundError(Messages.SHOW_KEY.format(key))

        if isinstance(tasks, list):
            for task in tasks[:]:
                if user.nick != task.author and user not in task.responsible:
                    tasks.remove(task)
            return tasks

        if user.nick != tasks.author and user.nick not in tasks.responsible:
            raise AccessDeniedError(Messages.CANNOT_SEE_TASK)
        return tasks

    @log
    def remove_task(self, key, recursive, rem_que_flag=False):
        """
        This method using for removing task
        :param key: access key
        :param recursive: flag, which mean executing operation for sub tasks
        if True
        :param rem_que_flag: flag, which mean that removing task occurs
         when deleting queue
         :raise AppError
        :return: tasks
        """
        remover = self.get_online_user()
        task = self.get_task(key)
        try:
            tasks = self.task_controller.remove_task(task, remover, recursive)

        except AppError as e:
            raise e

        if rem_que_flag is False:
            for task in tasks:
                queue = self.queue_controller.get_queue_by_key(task.queue)
                self.queue_controller.unlink_queue_and_task(queue, task)

        self.delete_link_with_users(tasks, remover, Messages.TASK_WAS_DELETED)
        return tasks

    @log
    def delete_link_with_users(self, tasks, author, message):
        """
        This method using for
        :param tasks:
        :param author: tasks author
        :param message: message which send to user
        :return: None
        """
        for task in tasks:
            while task.responsible:
                nick = task.responsible.pop()
                user = self.user_controller.find_user(nick=nick)
                self.user_controller.unlink_responsible_and_task(user, task)
                self.user_controller.notify_user(user,
                                                 message.format(task.name,
                                                                task.key,
                                                                task.author))
            if author is not None:
                self.user_controller.unlink_author_and_task(author, task)
                self.user_controller.notify_user(author,
                                                 message.format(task.name,
                                                                task.key,
                                                                task.author))

    @log
    def activate_task(self, key):
        """
        This method using for activating task by key
        :param key: access key
        :raise: TaskNotFoundError, ActivationTaskError
        :return: activated task
        """
        user = self.get_online_user()
        task = self.task_controller.find_task(key=key)
        if task is None:
            raise TaskNotFoundError(Messages.SHOW_KEY.format(key))

        if user.nick not in task.responsible:
            raise ActivationTaskError(Messages.CANNOT_ACTIVATE)

        if key in user.tasks_responsible:
            raise ActivationTaskError(Messages.ALREADY_CONFIRMED)

        self.user_controller.link_responsible_with_task(user, task)
        self.task_controller.activate_task(task)

        author = self.user_controller.find_user(nick=task.author)
        if author:
            message = (Messages.USER_CONFIRMED.format(user.nick, task.name,
                                                      task.key))

            self.user_controller.notify_user(author, message)

        return task

    @log
    def get_user_tasks(self):
        """
        This get all online user tasks
        :return: author tasks, responsible tasks
        """
        user = self.get_online_user()
        author_tasks = []
        for key in user.tasks_author:
            task = self.task_controller.find_task(key=key)
            if task:
                author_tasks.append(task)
        responsible_tasks = []
        for key in user.tasks_responsible:
            task = self.task_controller.find_task(key=key)
            if task:
                responsible_tasks.append(task)
        return author_tasks, responsible_tasks

    @log
    def get_responsible_diff(self, new, old):
        """
        This method
        :param new: new responsible user
        :param old: old responsible user
        :return: diff_old - user which suspended from participation
                 diff_new - user which invite
        """
        str_olds = [user.nick for user in old]
        str_news = [user.nick for user in new]
        diff_old = []
        diff_new = []
        for str_old in str_olds:
            if str_old not in str_news:
                diff_old.append(str_old)
        for str_new in str_news:
            if str_new not in str_olds:
                diff_new.append(str_new)
        return diff_old, diff_new

    @log
    def find_users_by_name_list(self, name_list):
        """
        This method using for
        :param name_list: list of users nicks
        :return: list of users
        """
        users = []
        if name_list == Constants.UNDEFINED:
            return users
        if name_list:
            for name in name_list:
                user = self.user_controller.find_user(nick=name)
                if user is None:
                    raise AppError(Messages.USER_NOT_FOUND.format(name))
                users.append(user)
        return users

    # functions for work with plans
    @log
    def add_plan(self, key, name, period, time, reminder):
        """
        This method using for crating plan entity
        :param key: access key
        :param name: plan name
        :param period:
        :param time: time when plan create task
        :param reminder:
        :return: created plan
        """
        author = self.get_online_user()
        return self.plan_controller.create_plan(key, author, name, period,
                                                time, reminder)

    @log
    def del_plan(self, key):
        """
        This method using for deleting plan
        :param key: access key
        :return:
        """
        return self.plan_controller.delete_plan(key)

    @log
    def edit_plan(self, key, new_name, period, time, reminder):
        return self.plan_controller.edit_plan(key, new_name, period, time,
                                              reminder)

    @log
    def get_plans(self):
        """
        This method using for getting online users plans
        :return: online users plans
        """
        return self.plan_controller.get_user_plans(self.get_online_user())
