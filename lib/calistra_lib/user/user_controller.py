from datetime import datetime as dt

TIME_FORMAT = '%d.%m.%Y.%H:%M:%S'


class UserController:
    def __init__(self, users_storage):
        self.users_storage = users_storage

    def add_user(self, nick):
        added_user = self.users_storage.add_user(nick)
        self.users_storage.save_users()
        return added_user

    def clear_user_notifications(self, user, quantity):
        if quantity is None:
            user.notifications.clear()
        else:
            if quantity > len(user.notifications):
                raise ValueError('')
            for i in range(quantity):
                user.notifications.pop(i)
        self.users_storage.save_users()

    def clear_new_messages(self, user):
        user.notifications += user.new_messages
        user.new_messages.clear()
        self.users_storage.save_users()

    def link_queue_with_user(self, user, queue):
        user = self.find_user(nick=user.nick)
        user.queues.append(queue.key)
        self.users_storage.save_users()

    def unlink_queue_and_user(self, user, queue):
        user = self.find_user(nick=user.nick)
        for _queue in user.queues:
            if _queue == queue.key:
                user.queues.remove(_queue)
        self.users_storage.save_users()

    def link_task_with_responsible(self, responsible, task):
        user = self.find_user(nick=responsible.nick)
        user.tasks_responsible.append(task.key)
        self.users_storage.save_users()

    def unlink_task_and_responsible(self, responsible, task):
        user = self.find_user(nick=responsible.nick)
        for key in user.tasks_responsible:
            if key == task.key:
                user.tasks_responsible.remove(key)
        self.users_storage.save_users()

    def link_task_with_author(self, author, task):
        user = self.find_user(nick=author.nick)
        user.tasks_author.append(task.key)
        self.users_storage.save_users()

    def unlink_task_and_author(self, author, task):
        user = self.find_user(nick=author.nick)
        for key in user.tasks_author:
            if key == task.key:
                user.tasks_author.remove(key)
        self.users_storage.save_users()

    def find_user(self, nick=None, uid=None):
        if uid is None:
            if nick is None:
                return None
            return self.users_storage.get_user_by_nick(nick)
        return self.users_storage.get_user_by_uid(uid)

    def notify_user(self, user, message):
        message = ''.join([dt.now().strftime(TIME_FORMAT), ': ', message])
        if user:
            user.new_messages.append(message)
            self.users_storage.save_users()
