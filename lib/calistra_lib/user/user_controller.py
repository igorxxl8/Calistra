from datetime import datetime as dt

try:
    from lib.calistra_lib.constants import Constants
except ImportError:
    from calistra_lib.constants import Constants


class UserController:
    def __init__(self, users_storage):
        self.users_storage = users_storage

    def add_user(self, nick, uid):
        user = self.users_storage.add_user(nick, uid)
        self.users_storage.save_users()
        return user

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

    def link_user_with_queue(self, user, queue):
        user.queues.append(queue.key)
        self.users_storage.save_users()

    def unlink_user_and_queue(self, user, queue):
        for _queue in user.queues:
            if _queue == queue.key:
                user.queues.remove(_queue)
                break

        self.users_storage.save_users()

    def link_responsible_with_task(self, responsible, task):
        responsible.tasks_responsible.append(task.key)
        self.users_storage.save_users()

    def unlink_responsible_and_task(self, responsible, task):
        for key in responsible.tasks_responsible:
            if key == task.key:
                responsible.tasks_responsible.remove(key)
                break

        self.users_storage.save_users()

    def link_author_with_task(self, author, task):
        user = self.find_user(nick=author.nick)
        user.tasks_author.append(task.key)
        self.users_storage.save_users()

    def unlink_author_and_task(self, author, task):
        for key in author.tasks_author:
            if key == task.key:
                author.tasks_author.remove(key)
                break

        self.users_storage.save_users()

    def find_user(self, nick=None, uid=None):
        if uid is None:
            if nick is None:
                return None
            return self.users_storage.get_user_by_nick(nick)
        return self.users_storage.get_user_by_uid(uid)

    def notify_user(self, user, message):
        message = ''.join(
            [
                dt.now().strftime(Constants.EXTENDED_TIME_FORMAT),
                ': ',
                message
            ]
        )

        if user:
            user.new_messages.append(message)
            self.users_storage.save_users()
