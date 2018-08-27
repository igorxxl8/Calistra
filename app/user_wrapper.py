"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""

from calistra_lib.storage.json_serializer import JsonDatabase
from calistra_lib.exceptions.base_exception import AppError


class UserWrapper:
    """
    Represent single user instance
    """
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
    """
    Store in database all user wrappers
    """
    def __init__(self, users_wrapper_file, online_user_file):
        self.online_user_db = JsonDatabase(online_user_file, [])
        self.users_wrapper_db = JsonDatabase(users_wrapper_file, [UserWrapper])
        self.users = self.users_wrapper_db.load()
        self.__online_user = self.online_user_db.load()

    def add_user(self, nick, password):
        """
        Function for add user to database
        :param nick:
        :param password:
        :return: None
        """
        if nick == 'guest':
            raise SaveUserError('name "guest" booked by program')
        for user in self.users:
            if user.nick == nick:
                raise SaveUserError('user "{}" already exists'.format(nick))

        self.users.append(UserWrapper(nick, password))
        self.record_users()

    def record_users(self):
        """
        Record users to database
        :return: None
        """
        self.users_wrapper_db.unload(self.users)

    @property
    def online_user(self):
        """
        Get online user
        :return: online user
        """
        return self.__online_user

    @online_user.setter
    def online_user(self, user=None):
        """
        Set online user
        :param user:
        :return: None
        """
        if user is None:
            self.online_user_db.unload("")
        else:
            self.online_user_db.unload(user.nick)

    def get_user(self, query: UserWrapper):
        """
        Get user by query
        :param query:
        :return: user
        """
        for user in self.users:
            if user == query:
                return user


class UserWrapperController:
    """
    Class which manipulate user instance
    """
    def __init__(self, users_storage: UserWrapperStorage):
        self.users_storage = users_storage

    def login(self, nick, password):
        """
        Method for login in system
        :param nick:
        :param password:
        :return: None
        """
        # check that anybody online
        online_user = self.users_storage.online_user
        if online_user:
            raise LoginError('there is already an '
                             'online user - "{}".'.format(online_user))

        # try to find user in user storage
        user = self.users_storage.get_user(UserWrapper(nick, password))
        if user is None:
            raise LoginError('please check, that you have entered your login'
                             ' and password correctly. ')

        self.users_storage.online_user = user

    def logout(self) -> None:
        """
        Method for logout
        :return: None
        """
        user = self.users_storage.online_user
        if not user:
            raise LogoutError('there are no online users.')
        self.users_storage.online_user = None


class SaveUserError(AppError):
    """
    Exception class for error appears when cannot save user
    """
    def __init__(self, message):
        message = ''.join(['Save user error: ', message])
        super().__init__(message)


class LoginError(AppError):
    """
    Exception class for error appears when cannot login user
    """
    def __init__(self, message):
        message = ''.join(['Log in error: ', message])
        super().__init__(message)


class LogoutError(AppError):
    """
    Exception class for error appears when cannot logout
    """
    def __init__(self, message):
        message = ''.join(['Log out error: ', message])
        super().__init__(message)
