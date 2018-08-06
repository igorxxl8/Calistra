"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""
import os
from random import randint
from datetime import datetime

try:
    from lib.calistra_lib.storage import json_serializer as js
    from lib.calistra_lib.user.user_storage import UserStorage
except ImportError:
    from calistra_lib.storage import json_serializer as js
    from calistra_lib.user.user_storage import UserStorage


# TODO: в самом начале использования нужно создавать файл с пустым списком!!!
# TODO: сделать загрузку пользователей из базы данных
FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
FILENAME = os.path.join(FOLDER, 'auth.json')
ONLINE = os.path.join(FOLDER, 'online_user.json')


def _make_uid():
    now = datetime.today()
    time_t = datetime.timetuple(now)
    uid = ''.join(
        [
            str(time_t.tm_year),
            str(time_t.tm_mon),
            str(time_t.tm_mday),
            str(time_t.tm_hour),
            str(time_t.tm_min),
            str(time_t.tm_sec),
            str(randint(0, 1000))
        ]
    )
    return int(uid)


def get_online_user_uid():
    return js.load([], ONLINE)


class UserWrapper:
    def __init__(self, nick, password):
        self.nick = nick
        self.password = password
        self.uid = _make_uid()

    def __eq__(self, other):
        return type(other) == type(self) and self.nick == other.nick and self.password == other.password

    def __ne__(self, other):
        return type(other) != type(self) or self.nick != other.nick or self.password != other.password


class UserWrapperStorage:

    def __init__(self):
        self.users = []
        self.load_users()
        self.users_storage = UserStorage()

    def load_users(self):
        self.users = js.load([UserWrapper], FILENAME)

    def add_user(self, new_user):
        for user in self.users:
            if user.nick == new_user.nick:
                raise SaveUserError(
                    "User with nick {} already exists".format(user.nick))

        self.users.append(new_user)
        self.users_storage.add_user(new_user.uid)

    def record_users(self):
        js.unload(self.users, FILENAME)

    def get_online_user(self):
        uid = get_online_user_uid()
        for user in self.users:
            if user.uid == uid:
                return user

    @staticmethod
    def set_online_user(user=None):
        if user is None:
            return js.unload(0, ONLINE)
        js.unload(user.uid, ONLINE)

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
        self.user_storage.set_online_user(user)

    def logout(self) -> None:
        user = self.user_storage.get_online_user()
        if not user:
            raise LogoutError("Unable to log out: There are no online users.")
        self.user_storage.set_online_user()

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