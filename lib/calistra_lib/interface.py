try:
    from lib.calistra_lib.constants import Constants
    from lib.calistra_lib.messages import Messages
    from lib.calistra_lib.queue.queue_controller import QueueController
    from lib.calistra_lib.queue.queue_storage import QueueStorage
    from lib.calistra_lib.task.task import TaskStatus
    from lib.calistra_lib.task.task_storage import TaskStorage
    from lib.calistra_lib.task.task_controller import TaskController
    from lib.calistra_lib.exceptions.base_exception import AppError
    from lib.calistra_lib.user.user_controller import UserController
    from lib.calistra_lib.user.user_storage import UserStorage
    from lib.calistra_lib.user.user import User
    from lib.calistra_lib.exceptions.access_exceptions import AccessDeniedError
    from lib.calistra_lib.exceptions.task_exceptions import (
        TaskNotFoundError,
        ActivationTaskError,
        TaskDeadlineError
    )
    from lib.calistra_lib.exceptions.queue_exceptions import (
        AddingQueueError,
        QueueNotFoundError
    )
except ImportError:
    from calistra_lib.constants import Constants
    from calistra_lib.messages import Messages
    from calistra_lib.queue.queue_controller import QueueController
    from calistra_lib.queue.queue_storage import QueueStorage
    from calistra_lib.task.task import TaskStatus
    from calistra_lib.task.task_storage import TaskStorage
    from calistra_lib.task.task_controller import TaskController
    from calistra_lib.exceptions.base_exception import AppError
    from calistra_lib.user.user_storage import UserStorage
    from calistra_lib.user.user_controller import UserController
    from calistra_lib.user.user import User
    from calistra_lib.exceptions.access_exceptions import AccessDeniedError
    from calistra_lib.exceptions.task_exceptions import (
        TaskNotFoundError,
        ActivationTaskError,
        TaskDeadlineError
    )
    from calistra_lib.exceptions.queue_exceptions import (
        AddingQueueError,
        QueueNotFoundError
    )
from datetime import datetime as dt


# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логирование


#                        Add    Set     Show    Logic
# TODO: 1) Name            +     +                +
# TODO: 2) Descrip         +     +                +
# TODO: 3) Author          +    (-)
# TODO: 4) Priority        +     +
# TODO: 5) Progress        +     +
# TODO: 6) Start           +     +                +
# TODO: 7) Deadline        +     +                +
# TODO: 8) Tags            +     +
# TODO: 9) Status         (-)    +
# TODO: 10) Reminder
# TODO: 11) Responsible    +     +
# TODO: 12) Parent         +     +
# TODO: 13) linked      ctrl,blc,dep
# TODO: запретить создание таск без имени
# TODO: рассылка уведомлений ответственным при добавлении и изменении задач
# TODO: написать перемещение задач в архив при выполнении
# TODO: перемещениче задач в проваленные при прошедшем дедлайне

def get_date(string):
    return dt.strptime(string, Constants.TIME_FORMAT)


class Interface:

    def __init__(self, online_user, queues_db, users_db, tasks_db):
        self.queue_controller = QueueController(QueueStorage(queues_db))
        self.task_controller = TaskController(TaskStorage(tasks_db))
        self.user_controller = UserController(UserStorage(users_db))
        self.online_user = self.user_controller.find_user(nick=online_user)

    # functions for work with user instance
    def get_online_user(self):
        if self.online_user is None:
            raise AccessDeniedError(Messages.SIGN_IN)
        return self.online_user

    def set_online_user(self, user_nick):
        self.online_user = self.user_controller.find_user(nick=user_nick)

    def add_user(self, nick, uid, queue_key):
        user = self.user_controller.add_user(nick, uid)
        self.add_queue(Constants.DEFAULT_QUEUE, queue_key, user)
        return user

    def clear_notifications(self, quantity=None):
        try:
            self.user_controller.clear_user_notifications(
                self.online_user, quantity)
        except ValueError as e:
            raise ValueError(e)

    def clear_new_messages(self):
        self.user_controller.clear_new_messages(self.online_user)

    def update_all(self):
        failed_tasks = self.task_controller.check_deadlines()
        controllers, blockers, dependents = self.task_controller.update_related_tasks()
        reminders = self.task_controller.check_reminders()

        for task in failed_tasks:
            queue = self.queue_controller.get_queue_by_key(task.queue)
            self.queue_controller.move_in_failed(queue, task)
            users = self.find_users_by_name_list(
                task.responsible + [task.author])

            self.send_message_to_users(
                users, Messages.TASK_WAS_FAILED.format(task.name)
            )

        for task in controllers:
            users = self.find_users_by_name_list(task.responsible+[task.author])
            self.send_message_to_users(
                users,
                Messages.TASK_WAS_UPDATED_BY_CONTROLLER.format(
                    task.name, task.status)
            )

        for task in blockers:
            users = self.find_users_by_name_list(task.responsible+[task.author])
            self.send_message_to_users(
                users,
                Messages.TASK_BLOCKERS_WERE_SOLVED.format(task.name)
            )


        for task in dependents:
            pass

    def send_message_to_users(self, users, message):
        for user in users:
            self.user_controller.notify_user(user, message)

    # functions for work with queue instance
    def add_queue(self, name, key, owner=None):
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

    def edit_queue(self, key, new_name):
        editor = self.get_online_user()
        try:
            return self.queue_controller.edit_queue(key, new_name, editor)
        except AppError as e:
            raise e

    def remove_queue(self, key, recursive):
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

    def get_user_queues(self):
        try:
            user = self.get_online_user()
            queues = self.queue_controller.get_user_queues(user)
        except AppError as e:
            raise e
        return queues

    def get_queue(self, queue_key, owner=None):
        if owner is None:
            owner = self.online_user
        if queue_key == Constants.UNDEFINED:
            queue = self.queue_controller.get_user_default_queue(owner)
        else:
            queue = self.queue_controller.get_queue_by_key(queue_key)
        if queue.owner != owner.uid:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_QUEUE)
        return queue

    def find_queues(self, name):
        user = self.get_online_user()
        queues = self.queue_controller.get_user_queues(user)
        result = []
        for queue in queues:
            if queue.name == name or queue.name.startswith(name):
                result.append(queue)
        return result

    # functions for work with task instance
    def create_task(self, name, queue_key, description, parent, related,
                    responsible, priority, progress, start, deadline, tags,
                    reminder, key):

        creating_time = dt.strftime(dt.now(), Constants.EXTENDED_TIME_FORMAT)
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

    def edit_task(self, key, name, description, parent, related,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):

        editing_time = dt.strftime(dt.now(), Constants.EXTENDED_TIME_FORMAT)
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
                users = self.find_users_by_name_list(task.responsible + [task.author])
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

    def get_task(self, key, owner=None):
        if owner is None:
            owner = self.get_online_user()
        task = self.task_controller.get_task_by_key(key)
        if task.author != owner.nick and owner.nick not in task.responsible:
            raise AccessDeniedError(Messages.CANNOT_USE_SOMEONE_ELSE_TASK)
        return task

    def get_task_tree(self):
        pass

    def find_task(self, key=None, name=None):
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

    def remove_task(self, key, recursive, rem_que_flag=False):
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

    def delete_link_with_users(self, tasks, author, message):
        for task in tasks:
            while task.responsible:
                nick = task.responsible.pop()
                user = self.user_controller.find_user(nick=nick)
                self.user_controller.unlink_responsible_and_task(user, task)
                self.user_controller.notify_user(user,
                                                 message.format(task.name, task.key, task.author))
            if author is not None:
                self.user_controller.unlink_author_and_task(author, task)
                self.user_controller.notify_user(author, message.format(task.name, task.key, task.author))

    def activate_task(self, key):
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

    def get_user_tasks(self):
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

    def get_responsible_diff(self, new, old):
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

    def find_users_by_name_list(self, name_list):
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

    #
    #
    # Приступить после окончания работы с задачами
    def add_plan(self):
        pass

    def del_plan(self):
        pass

    def edit_plan(self):
        pass
