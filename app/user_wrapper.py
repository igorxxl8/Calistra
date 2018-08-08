"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""

try:
    from lib.calistra_lib.storage import json_serializer as js
except ImportError:
    from calistra_lib.storage import json_serializer as js


class UserWrapper:
    def __init__(self, nick, password):
        self.nick = nick
        self.password = password

    def __eq__(self, other):
        return (type(other) == type(self) and
                self.nick == other.nick and
                self.password == other.password)

    def __ne__(self, other):
        return (type(other) != type(self) or
                self.nick != other.nick or
                self.password != other.password)


class UserWrapperStorage:

    def __init__(self, users_wrapper_db, online_user_db):
        self.online_user_db = online_user_db
        self.users_wrapper_db = users_wrapper_db
        self.users = self.load_users()

    def load_users(self):
        return js.load([UserWrapper], self.users_wrapper_db)

    def add_user(self, nick, password):
        for user in self.users:
            if user.nick == nick:
                raise SaveUserError(
                    "User with nick {} already exists".format(user.nick))

        new_user = UserWrapper(nick, password)
        self.users.append(new_user)
        self.record_users()

    def record_users(self):
        js.unload(self.users, self.users_wrapper_db)

    def get_online_user(self):
        nick = js.load([], self.online_user_db)
        for user in self.users:
            if user.nick == nick:
                return user

    def set_online_user(self, user=None):
        if user is None:
            return js.unload(0, self.online_user_db)
        js.unload(user.nick, self.online_user_db)

    def get_user(self, query):
        for user in self.users:
            if user == query:
                return user


class UserWrapperController:
    def __init__(self, users_storage: UserWrapperStorage):
        self.users_storage = users_storage

    def login(self, user: UserWrapper):
        # check that anybody online
        online_user = self.users_storage.get_online_user()
        if online_user:
            raise LoginError('Unable to login: '
                             'There is already an '
                             'online user - {}.'.format(online_user.nick))

        # try to find user in user storage
        user = self.users_storage.get_user(user)
        if user is None:
            raise LoginError('Unable to log in. Please check that you have'
                             ' entered your login and password correctly. ')
        self.users_storage.set_online_user(user)

    def logout(self) -> None:
        user = self.users_storage.get_online_user()
        if not user:
            raise LogoutError("Unable to log out: There are no online users.")
        self.users_storage.set_online_user()

    def set_new_nick(self, user: UserWrapper):
        pass

    def set_new_pasw(self, user: UserWrapper):
        pass


class SaveUserError(Exception):
    def __init__(self, message):
        self.message = message


class LoginError(Exception):

    def __init__(self, message):
        self.message = message


class LogoutError(Exception):

    def __init__(self, message):
        self.message = message
