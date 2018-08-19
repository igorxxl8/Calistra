"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""

try:
    from lib.calistra_lib.storage.database import Database
    from lib.calistra_lib.exceptions.base_exception import AppError
except ImportError:
    from calistra_lib.storage.database import Database
    from calistra_lib.exceptions.base_exception import AppError


# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логирование

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

    def __init__(self, users_wrapper_db: Database, online_user_db: Database):
        self.online_user_db = online_user_db
        self.users_wrapper_db = users_wrapper_db
        self.users = self.users_wrapper_db.load()
        self.__online_user = online_user_db.load()

    def add_user(self, nick, password):
        if nick == 'guest':
            raise SaveUserError('name "guest" booked by program')
        for user in self.users:
            if user.nick == nick:
                raise SaveUserError('user "{}" already exists'.format(nick))

        self.users.append(UserWrapper(nick, password))
        self.record_users()

    def record_users(self):
        self.users_wrapper_db.unload(self.users)

    @property
    def online_user(self):
        return self.__online_user

    @online_user.setter
    def online_user(self, user=None):
        if user is None:
            self.online_user_db.unload("")
        else:
            self.online_user_db.unload(user.nick)

    def get_user(self, query: UserWrapper):
        for user in self.users:
            if user == query:
                return user


class UserWrapperController:
    def __init__(self, users_storage: UserWrapperStorage):
        self.users_storage = users_storage

    def login(self, nick, password):
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
        user = self.users_storage.online_user
        if not user:
            raise LogoutError('there are no online users.')
        self.users_storage.online_user = None

    def set_new_nick(self, user: UserWrapper):
        pass

    def set_new_pasw(self, user: UserWrapper):
        pass


class SaveUserError(AppError):
    def __init__(self, message):
        message = ''.join(['Save user error: ', message])
        super().__init__(message)


class LoginError(AppError):
    def __init__(self, message):
        message = ''.join(['Log in error: ', message])
        super().__init__(message)


class LogoutError(AppError):
    def __init__(self, message):
        message = ''.join(['Log out error: ', message])
        super().__init__(message)
