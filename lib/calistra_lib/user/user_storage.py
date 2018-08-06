from .user_model import User
import os

try:
    from lib.calistra_lib.storage import json_serializer as js
except ImportError:
    from calistra_lib.storage import json_serializer as js


USERS_FILE = os.path.join(os.environ['HOME'], 'calistra_data', 'users.json')


class UserStorage:
    def __init__(self):
        self.users = []
        self.load_users()

    def load_users(self):
        self.users = js.load([User], USERS_FILE)

    def record_users(self):
        js.unload(self.users, USERS_FILE)

    def add_user(self, user_uid):
        self.users.append(User(user_uid))
        self.record_users()
