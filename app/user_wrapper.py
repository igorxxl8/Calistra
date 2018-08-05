"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""
try:
    from lib.calistra_lib import json_serializer as js
except ImportError:
    from calistra_lib import json_serializer as js

import os

FILENAME = os.path.join(os.environ['HOME'], 'users.json')


class UserWrapper:
    def __init__(self, nick, password):
        self.nick = nick
        self.password = password
        self.online = False

    def __eq__(self, other):
        return type(other) == type(self) and self.nick == other.nick and self.password == other.password

    def __ne__(self, other):
        return type(other) != type(self) or self.nick != other.nick or self.password != other.password

    def change_online_status(self):
        self.online = not self.online


class UserWrapperStorage:

    def __init__(self):
        self.users = []
        self.load_users()

    def load_users(self):
        with open(FILENAME, 'r') as file:
            s = file.read()
        self.users = js.from_json([UserWrapper], s)

    # TODO: в самом начале использования нужно создавать файл с пустым списком!!!
    # TODO: сделать загрузку пользователей из базы данных

    def add_user(self, new_user):
        for user in self.users:
            if user.nick == new_user.nick:
                raise SaveUserError(
                    "User with nick {} already exists".format(user.nick))

        self.users.append(new_user)

    def record_users(self):
        with open(FILENAME, 'w') as file:
            file.write(js.to_json(self.users))

    # TODO: сделать запись пользователей в базу данных

    def get_online_user(self):
        for user in self.users:
            if user.online:
                return user

    def get_user(self, query):
        for user in self.users:
            if user == query:
                return user


class SaveUserError(Exception):
    def __init__(self, message):
        self.message = message


class UserWrapperController:
    def __init__(self, user_storage: UserWrapperStorage):
        self.user_storage = user_storage

    def login(self, user: UserWrapper) -> None:
        # check that anybody online
        online_user = self.user_storage.get_online_user()
        if online_user:
            raise LoginError('Unable to login: '
                             'There is already an '
                             'online user - {}.'.format(online_user.nick))

        # try to find user in user storage
        user = self.user_storage.get_user(user)
        if user is None:
            raise LoginError('Unable to log in. Please check that you have'
                             ' entered your login and password correctly. ')
        user.change_online_status()
        self.user_storage.record_users()

    def logout(self) -> None:
        user = self.user_storage.get_online_user()
        if not user:
            raise LogoutError("Unable to log out: There are no online users.")
        user.change_online_status()
        # TODO: добавить сохранение состояния
        self.user_storage.record_users()

    def set_new_nick(self, user: UserWrapper):
        pass

    def set_new_pasw(self, user: UserWrapper):
        pass


class LoginError(Exception):

    def __init__(self, message):
        self.message = message


class LogoutError(Exception):

    def __init__(self, message):
        self.message = message