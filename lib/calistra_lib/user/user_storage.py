from .user_model import User

try:
    from lib.calistra_lib.storage import json_serializer as js
except ImportError:
    from calistra_lib.storage import json_serializer as js


# TODO: обобщить метод загрузки данных


class UserStorage:
    def __init__(self, users_file):
        self.users_file = users_file
        self.users = self.load_users()

    def load_users(self):
        return js.load([User], self.users_file)

    def record_users(self):
        js.unload(self.users, self.users_file)

    def add_user(self, nick):
        self.users.append(User(nick))
        self.record_users()
