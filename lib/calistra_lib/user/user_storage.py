from .user import User

try:
    from lib.calistra_lib.storage.database import Database
except ImportError:
    from calistra_lib.storage.database import Database


# TODO: обобщить метод загрузки данных


class UserStorage:
    def __init__(self, users_db: Database):
        self.users_db = users_db
        self.users = users_db.load()

    def record_users(self):
        self.users_db.unload(self.users)

    def add_user(self, nick):
        self.users.append(User(nick))
        self.record_users()
