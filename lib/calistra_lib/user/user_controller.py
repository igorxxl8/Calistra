"""
This module contains class UserController which describe instance for
creating, manipulating, editing users entities
"""


from datetime import datetime as dt
from calistra_lib.constants import Time
from calistra_lib.user.user import User


class UserController:
    """This class describe instance and methods for work with user entities"""
    def __init__(self, users_storage):
        self.users_storage = users_storage

    def add_user(self, nick, uid):
        user = User(nick, uid)
        self.users_storage.add_user(user)
        self.users_storage.save_users()
        return user

    def clear_user_notifications(self, user, quantity):
        """This method delete all user notifications
        :param user:
        :param quantity: number of deleting notifications
        """
        if quantity is None:
            user.notifications.clear()
        else:
            if quantity > len(user.notifications):
                raise ValueError('')
            for i in range(quantity):
                user.notifications.pop(i)
        self.users_storage.save_users()

    def clear_new_messages(self, user):
        """
        This method delete new messages and move they in notifications
        :param user:
        :return:
        """
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
        """

        :param responsible:
        :param task:
        :return:
        """
        for key in responsible.tasks_responsible:
            if key == task.key:
                responsible.tasks_responsible.remove(key)
                break

        self.users_storage.save_users()

    def link_author_with_task(self, author, task):
        """
        This method create link between task and it author
        :param author:
        :param task:
        :return: None
        """
        user = self.find_user(nick=author.nick)
        user.tasks_author.append(task.key)
        self.users_storage.save_users()

    def unlink_author_and_task(self, author, task):
        """
        This method delete link between task and it author
        :param author: task author
        :param task:
        :return: None
        """
        for key in author.tasks_author:
            if key == task.key:
                author.tasks_author.remove(key)
                break

        self.users_storage.save_users()

    def find_user(self, nick=None, uid=None):
        """
        This method using for search user in storage by nick or uid
        :param nick: user nick
        :param uid: user unique identifier
        :return: requested user if it found or None
        """
        if uid is None:
            if nick is None:
                return None
            return self.users_storage.get_user_by_nick(nick)
        return self.users_storage.get_user_by_uid(uid)

    def notify_user(self, user, message, show_time=True):
        """
        This method send notification message to user
        :param user:
        :param message: text of notification
        :param show_time: flag, which mean showing time if it True
        :return:
        """
        if show_time:
            time = dt.now().strftime(Time.EXTENDED_TIME_FORMAT)
            message = ''.join([time, ': ', message])

        if user:
            user.new_messages.append(message)
            self.users_storage.save_users()
