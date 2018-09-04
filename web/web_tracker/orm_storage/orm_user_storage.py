from calistra_lib.user.user_storage_interface import IUserStorage
from web_tracker.models import User


class ORMUserStorage(IUserStorage):
    def __init__(self):
        super().__init__(User.objects.all())

    def get_user_by_nick(self, nick):
        try:
            return self.users.get(nick=nick)
        except Exception:
            return None

    def get_user_by_uid(self, uid):
        return self.users.get(uid=uid)

    def save_users(self):
        for user in self.users:
            user.save()

    def add_user(self, user):
        self.users.create(
            nick=user.nick,
            uid=user.uid
        )
