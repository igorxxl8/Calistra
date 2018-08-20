from .user import User

try:
    from lib.calistra_lib.storage.database import Database
except ImportError:
    from calistra_lib.storage.database import Database


# TODO: обобщить метод загрузки данных
# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование

class UserStorage:
    def __init__(self, users_db: Database):
        self.users_db = users_db
        self.users = users_db.load()

    def get_user_by_nick(self, nick):
        for user in self.users:
            if user.nick == nick:
                return user

    def get_user_by_uid(self, uid):
        for user in self.users:
            if user.uid == uid:
                return uid

    def save_users(self):
        self.users_db.unload(self.users)

    def add_user(self, nick, uid):
        self.users.append(User(nick, uid))
        return self.users[-1]
