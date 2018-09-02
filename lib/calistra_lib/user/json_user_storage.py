"""This module contains class JsonUserStorage which describe instancesuitable
for store users in files in json format"""

from calistra_lib.user.user import User
from calistra_lib.storage.json_serializer import JsonDatabase
from calistra_lib.user.user_storage_interface import IUserStorage


class JsonUserStorage(IUserStorage):
    """This class represent instance for storing users in
    file in json format"""
    def __init__(self, users_file):
        self.users_db = JsonDatabase(users_file, [User])
        super().__init__(self.users_db.load())

    def get_user_by_nick(self, nick):
        """
        This method getting user from database by his nick
        :param nick: parametr for finding
        :return: user which has suitable nick
        """
        for user in self.users:
            if user.nick == nick:
                return user

    def get_user_by_uid(self, uid):
        """
        This method using for getting user from database by his uid
        :param uid: user universal identifier
        :return: requested user
        """
        for user in self.users:
            if user.uid == uid:
                return uid

    def save_users(self):
        """
        This method save user in database
        :return: None
        """
        self.users_db.unload(self.users)

    def add_user(self, user):
        """
        This method append user in users list
        :param user: added user
        :return: None
        """
        self.users.append(user)
