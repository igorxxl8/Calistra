from .user_wrapper import UserWrapper

# TODO: сделать документирование


class UserWrapperController:

    def __init__(self, user_wrapper_storage):
        self.user_wrapper_storage = user_wrapper_storage

    def login_user(self, nick, pasw):
        # check that anybody online
        online_user = self.user_wrapper_storage.get_online_user()
        if online_user:
            raise LoginError('Unable to login: '
                             'There is already an online user.')

        # get user with you want to login
        user = self.user_wrapper_storage.get_user_by_nick(nick)
        if not user:
            raise LoginError('Unable to login: There are no registered users')
        if user.pasw != pasw:
            raise LoginError("Unable to login: Check the entered nickname"
                             " and password for correctness")
        user.change_online_status()

    def logout_user(self):
        user = self.user_wrapper_storage.get_online_user()
        if not user:
            raise LogoutError("Unable to log out: There are no online users.")
        user.change_online_status()

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
