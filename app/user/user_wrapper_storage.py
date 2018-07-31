import json
from . import UserWrapper

# TODO: сделать документирование


class UserWrapperStorage:

    def __init__(self, users=None):
        self.users = users
        if not users:
            self.load_users()

    def load_users(self):
        pass
    # TODO: сделать загрузку пользователей из базы данных

    def save_user(self, user):
        for _ in self.users:
            if user.nick == _.nick:
                raise SaveUserError(
                    "User with nick {} already exists".format(user.nick)
                )
        self.users.append(user)

    def record_users(self):
        pass
    # TODO: сделать запись пользователей в базу данных

    def get_user_by_nick(self, nick):
        if not self.users:
            return
        for user in self.users:
            if user.nick == nick:
                return user

    def get_online_user(self):
        if not self.users:
            return
        for user in self.users:
            if user.online:
                return user


class SaveUserError(Exception):
    def __init__(self, message):
        self.message = message
