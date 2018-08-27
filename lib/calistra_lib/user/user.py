"""This module contains class User for represent a single user entity"""


class User:
    """This class describe single user"""

    def __init__(self, nick, uid):
        self.uid = uid
        self.nick = nick
        self.queues = []
        self.tasks_author = []
        self.tasks_responsible = []
        self.notifications = []
        self.new_messages = []
