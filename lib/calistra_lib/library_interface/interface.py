try:
    from lib.calistra_lib.task.task_storage import TaskStorage
    from lib.calistra_lib.task.task_controller import TaskController
    from lib.calistra_lib.task.task_exceptions import QueueError, TaskError
    from lib.calistra_lib.user.user_controller import UserController
    from lib.calistra_lib.user.user_storage import UserStorage
    from lib.calistra_lib.user.user import User
except ImportError:
    from calistra_lib.task.task_storage import TaskStorage
    from calistra_lib.task.task_controller import TaskController
    from calistra_lib.task.task_exceptions import QueueError, TaskError
    from calistra_lib.user.user_storage import UserStorage
    from calistra_lib.user.user_controller import UserController
    from calistra_lib.user.user import User
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
# TODO: 7) Deadline        +     +
# TODO: 8) Tags            +     +
# TODO: 9) Status         (-)    +
# TODO: 10) Reminder
# TODO: 11) Responsible _работаю
# TODO: 12) Parent         +     +
# TODO: 13) linked
# TODO: запретить создание таск без имени
# TODO: рассылка уведомлений ответственным при добавлении и изменении задач
# TODO: написать перемещение задач в архив при выполнении
# TODO: перемещениче задач в проваленные при прошедшем дедлайне
TIME_FORMAT = '%d.%m.%Y.%H:%M'


def get_date(string):
    return dt.strptime(string, TIME_FORMAT)


class Interface:

    def __init__(self, online_user, users_db, task_db):
        self.task_controller = TaskController(TaskStorage(task_db))
        self.user_controller = UserController(UserStorage(users_db))
        self.online_user = self.user_controller.find_user(nick=online_user)
        if self.online_user is None:
            self.online_user = User('guest')
            self.online_user.uid = '0'

    def add_user(self, nick):
        new_user = self.user_controller.add_user(nick)
        self.add_queue('default', new_user.uid, new_user)
        return new_user

    def add_queue(self, name, key, owner=None):
        if owner is None:
            owner = self.online_user
        if owner.nick == 'guest':
            raise QueueError('You cannot add new queue. Please sign in system')
        try:
            new_queue = self.task_controller.add_queue(name, key, owner)
        except QueueError as e:
            raise QueueError(e)
        else:
            self.user_controller.link_queue_with_user(owner, new_queue)
            return new_queue

    def edit_queue(self, key, new_name):
        editor = self.online_user
        try:
            return self.task_controller.edit_queue(key, new_name, editor)
        except QueueError as e:
            raise QueueError(e)

    def del_queue(self, key, recursive):
        owner = self.online_user
        try:
            queue = self.task_controller.del_queue(key, recursive, owner)
        except QueueError as e:
            raise QueueError(e)
        else:
            self.user_controller.unlink_queue_and_user(owner, queue)
            print(queue.tasks)
            if queue.tasks:
                # TODO: не оповещает пользователей задач которые не подзадачи
                self.unlink_all_users(queue.tasks, owner)
            return queue

    def get_user_queues(self):
        try:
            queues = self.task_controller.get_queues_by_owner(self.online_user)
        except QueueError as e:
            raise QueueError(e)
        else:
            return queues

    def get_queue_tasks(self, queue_key):
        owner = self.online_user
        try:
            tasks = self.task_controller.get_queue_tasks(queue_key, owner)
        except QueueError as e:
            raise QueueError(e)
        else:
            return tasks

    def add_task(self, name, queue_key, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):

        author = self.online_user
        try:
            responsible_users = self.get_responsible_users(responsible)

            new_task = self.task_controller.add_task(
                author=author, name=name, queue_key=queue_key,
                description=description, parent=parent, linked=linked,
                responsible=responsible, priority=priority, progress=progress,
                start=start, deadline=deadline, tags=tags, reminder=reminder,
                key=key
            )
        except TaskError as e:
            raise TaskError(e)
        else:
            for user in responsible_users:
                self.user_controller.link_task_with_responsible(
                    responsible=user, task=new_task)
            if self.online_user.nick != 'guest':
                self.user_controller.link_task_with_author(author, new_task)
            return new_task

    def edit_task(self, key, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):
        editor = self.online_user
        try:
            edited_task = self.task_controller.find_task(key=key)
            old_responsible_users = self.get_responsible_users(
                edited_task.responsible)
            new_responsible_users = self.get_responsible_users(responsible)
            task = self.task_controller.edit_task(
                key=key, editor=editor, name=name, description=description,
                parent=parent, linked=linked, priority=priority,
                progress=progress, start=start, deadline=deadline, tags=tags,
                reminder=reminder, status=status, responsible=responsible)

        except TaskError as e:
            raise TaskError(e)
        else:
            unresp, resp = self.get_responsible_diff(
                new_responsible_users, old_responsible_users)
            new_responsible_users = self.get_responsible_users(resp)
            old_responsible_users = self.get_responsible_users(unresp)
            # TODO: где то здесь неправильно пишется в json, найти и исправить
            for user in old_responsible_users:
                self.user_controller.unlink_task_and_responsible(
                    responsible_nick=user.nick, task=task
                )
            for user in new_responsible_users:
                self.user_controller.link_task_with_responsible(
                    responsible=user, task=task)
            return task

    def del_task(self, key, recursive):
        owner = self.online_user
        try:
            tasks = self.task_controller.del_task(owner, key, recursive)
        except TaskError as e:
            raise TaskError(e)
        else:
            self.unlink_all_users(tasks, owner)
            return tasks

    def unlink_responsible(self, task):
        while task.responsible:
            self.user_controller.unlink_task_and_responsible(
                responsible_nick=task.responsible.pop(), task=task)

    def unlink_author(self, author, task):
        if author is not None:
            self.user_controller.unlink_task_and_author(author, task)

    def unlink_all_users(self, tasks, owner=None):
        for task in tasks:
            self.unlink_responsible(task)
            self.unlink_author(owner, task)

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

    def get_responsible_users(self, responsible):
        responsible_users = []
        if responsible == '?':
            return responsible_users
        if responsible:
            for person in responsible:
                user = self.user_controller.find_user(nick=person)
                if user is None:
                    raise TaskError(
                        'User "{}" didn\'t found'.format(person))
                responsible_users.append(user)
        return responsible_users

    #
    #
    # Приступить после окончания работы с задачами
    def add_plan(self):
        pass

    def del_plan(self):
        pass

    def edit_plan(self):
        pass
