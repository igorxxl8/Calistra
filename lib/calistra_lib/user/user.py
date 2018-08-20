# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование


class User:
    def __init__(self, nick, uid):
        self.uid = uid
        self.nick = nick
        self.queues = []
        self.tasks_author = []
        self.tasks_responsible = []
        self.notifications = []
        self.new_messages = []
