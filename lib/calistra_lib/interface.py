try:
    from lib.calistra_lib.task.task import TaskStatus
    from lib.calistra_lib.task.task_storage import TaskStorage
    from lib.calistra_lib.task.task_controller import TaskController
    from lib.calistra_lib.exceptions.base_exception import AppError
    from lib.calistra_lib.user.user_controller import UserController
    from lib.calistra_lib.user.user_storage import UserStorage
    from lib.calistra_lib.user.user import User
    from lib.calistra_lib.exceptions.access_exceptions import AccessDeniedError
    from lib.calistra_lib.exceptions.task_exceptions import TaskNotFoundError
    from lib.calistra_lib.exceptions.queue_exceptions import (
        AddingQueueError,
        QueueNotFoundError
    )
except ImportError:
    from calistra_lib.task.task import TaskStatus
    from calistra_lib.task.task_storage import TaskStorage
    from calistra_lib.task.task_controller import TaskController
    from calistra_lib.exceptions.base_exception import AppError
    from calistra_lib.user.user_storage import UserStorage
    from calistra_lib.user.user_controller import UserController
    from calistra_lib.user.user import User
    from calistra_lib.exceptions.access_exceptions import AccessDeniedError
    from calistra_lib.exceptions.task_exceptions import TaskNotFoundError
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
# TODO: 13) linked
# TODO: запретить создание таск без имени
# TODO: рассылка уведомлений ответственным при добавлении и изменении задач
# TODO: написать перемещение задач в архив при выполнении
# TODO: перемещениче задач в проваленные при прошедшем дедлайне
TIME_FORMAT = '%d.%m.%Y.%H:%M'
EXTENDED_TIME_FORMAT = '%d.%m.%Y.%H:%M:%S'
UNDEFINED = '?'
GUEST = 'guest'
GUEST_UID = '0'
DEFAULT_QUEUE = 'default'


def get_date(string):
    return dt.strptime(string, TIME_FORMAT)


class Interface:

    def __init__(self, online_user, users_db, task_db):
        self.task_controller = TaskController(TaskStorage(task_db))
        self.user_controller = UserController(UserStorage(users_db))
        self.online_user = self.user_controller.find_user(nick=online_user)
        if self.online_user is None:
            self.online_user = User(GUEST)
            self.online_user.uid = GUEST_UID

    def clear_notifications(self, quantity=None):
        try:
            self.user_controller.clear_user_notifications(
                self.online_user, quantity)
        except ValueError as e:
            raise ValueError(e)

    def set_online_user(self, user_nick):
        self.online_user = self.user_controller.find_user(nick=user_nick)

    def update_all(self):
        failed_tasks = self.task_controller.update_tasks()
        reminders = self.task_controller.check_reminders()
        for task in failed_tasks:
            pass

        #    self.

    def add_user(self, nick):
        new_user = self.user_controller.add_user(nick)
        self.add_queue(DEFAULT_QUEUE, new_user.uid, new_user)
        return new_user

    def add_queue(self, name, key, owner=None):
        if owner is None:
            owner = self.online_user
        if owner.nick == GUEST:
            raise AddingQueueError('please sign in system')
        try:
            new_queue = self.task_controller.add_queue(name, key, owner)
        except AppError as e:
            raise AppError(e)
        else:
            self.user_controller.link_queue_with_user(owner, new_queue)
            return new_queue

    def edit_queue(self, key, new_name):
        editor = self.online_user
        try:
            return self.task_controller.edit_queue(key, new_name, editor)
        except AppError as e:
            raise AppError(e)

    def del_queue(self, key, recursive):
        user = self.online_user
        try:
            queue = self.task_controller.del_queue(key, recursive, user)
        except AppError as e:
            raise AppError(e)

        self.user_controller.unlink_queue_and_user(user, queue)
        all_tasks = queue.opened + queue.solved + queue.failed
        if all_tasks:
            for task in all_tasks:
                while task.responsible:
                    nick = task.responsible.pop()
                    user = self.user_controller.find_user(nick=nick)
                    self.user_controller.unlink_task_and_responsible(user, task)
                    self.user_controller.notify_user(
                        user,
                        'The task {} was deleted'.format(task.name)
                    )

                if user is not None:
                    self.user_controller.unlink_task_and_author(user, task)
                    
        return queue

    def get_user_queues(self):
        try:
            queues = self.task_controller.get_queues_by_owner(self.online_user)
        except AppError as e:
            raise AppError(e)
        return queues

    def get_queue(self, queue_key):
        queue = self.task_controller.get_queue_by_key(queue_key)
        if queue is None:
            raise QueueNotFoundError('key - {}'.format(queue_key))
        return queue

    def add_task(self, name, queue_key, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):
        create_time = dt.strftime(dt.now(), EXTENDED_TIME_FORMAT)
        author = self.online_user
        try:
            responsible_users = self.find_users_by_name_list(responsible)

            task = self.task_controller.add_task(
                author=author, name=name, queue_key=queue_key,
                description=description, parent=parent, linked=linked,
                responsible=responsible, priority=priority, progress=progress,
                start=start, deadline=deadline, tags=tags, reminder=reminder,
                key=key, create_time=create_time
            )
        except AppError as e:
            raise AppError(e)
        else:
            for user in responsible_users:
                self.user_controller.link_task_with_responsible(
                    responsible=user, task=task)
                message = ('User {} assigned you responsible for the task:'
                           ' "{}", key - {}'.format(author.nick, task.name, task.key))
                self.user_controller.notify_user(user, message)

            if self.online_user.nick != GUEST:
                self.user_controller.link_task_with_author(author, task)
            return task

    def edit_task(self, key, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):

        edit_time = dt.strftime(dt.now(), EXTENDED_TIME_FORMAT)
        editor = self.online_user

        try:
            task = self.task_controller.find_task(key=key)
            if task is None:
                raise TaskNotFoundError('key - {}'.format(key))

            if responsible is None:
                current_responsible = []
                new_responsible = []
            else:
                current_responsible = self.find_users_by_name_list(task.responsible)
                new_responsible = self.find_users_by_name_list(responsible)

            task = self.task_controller.edit_task(
                task=task, editor=editor, name=name, description=description,
                parent=parent, linked=linked, priority=priority,
                progress=progress, start=start, deadline=deadline, tags=tags,
                reminder=reminder, status=status, responsible=responsible,
                edit_time=edit_time
            )

        except AppError as e:
            raise AppError(e)
        else:
            dismissed_users, invited_users = self.get_responsible_diff(
                new_responsible, current_responsible)
            new_responsible = self.find_users_by_name_list(invited_users)
            current_responsible = self.find_users_by_name_list(dismissed_users)
            responsible_users = self.find_users_by_name_list(task.responsible)

            if status == TaskStatus.CLOSED:
                self.user_controller.unlink_task_and_author(editor, task)

            for user in current_responsible:
                self.user_controller.unlink_task_and_responsible(user, task)
                message = ('You are suspended from task execution:'
                           ' "{}".'.format(task.name))
                self.user_controller.notify_user(user, message)

            if editor.nick != task.author:
                author = self.user_controller.find_user(nick=task.author)
                self.user_controller.notify_user(
                    author, TaskController.EDITING_MESSAGE)

            for user in new_responsible:
                self.user_controller.link_task_with_responsible(user, task)
                message = ('User "{}" assigned you responsible for the task:'
                           ' "{}", key - {}'.format(editor.nick, task.name, task.key))
                self.user_controller.notify_user(user, message)

            for user in responsible_users:
                if user.nick == task.author:
                    continue
                self.user_controller.notify_user(
                    user, TaskController.EDITING_MESSAGE)

            # for user in responsible
            return task

    def find_task(self, key=None, name=None):
        user = self.online_user.nick
        tasks = self.task_controller.find_task(key=key, name=name)

        if tasks is None:
            raise TaskNotFoundError('key - {}'.format(key))

        if isinstance(tasks, list):
            for task in tasks:
                if user != task.author and user not in task.responsible:
                    tasks.remove(task)
            return tasks
        if user != tasks.author and user not in tasks.responsible:
            raise AccessDeniedError('you cannot see this task')
        return tasks

    def del_task(self, key, recursive):
        owner = self.online_user
        try:
            tasks = self.task_controller.del_task(owner, key, recursive)

        except AppError as e:
            raise AppError(e)

        else:
            for task in tasks:
                while task.responsible:
                    self.user_controller.unlink_task_and_responsible(
                        responsible=task.responsible.pop(), task=task)
                if owner is not None:
                    self.user_controller.unlink_task_and_author(owner, task)
            return tasks

    def get_user_tasks(self):
        author_tasks = []
        for key in self.online_user.tasks_author:
            task = self.task_controller.find_task(key=key)
            if task:
                author_tasks.append(task)
        responsible_tasks = []
        for key in self.online_user.tasks_responsible:
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
        if name_list == UNDEFINED:
            return users
        if name_list:
            for name in name_list:
                user = self.user_controller.find_user(nick=name)
                if user is None:
                    raise AppError(
                        'User not found: name - "{}"'.format(name))
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
