"""This module contains basic interface class IUserStorage for all classes
 which describe instance for saving plans"""


class IUserStorage:
    """This class represent basic interface for implementing classes which
    store users in database"""
    def get_user_by_nick(self, nick):
        """
        This method getting user from database by his nick
        :param nick: parametr for finding
        :return: user which has suitable nick
        """
        raise NotImplementedError()

    def get_user_by_uid(self, uid):
        """
        This method using for getting user from database by his uid
        :param uid: user universal identifier
        :return: requested user
        """
        raise NotImplementedError()

    def save_users(self):
        """
        This method save user in database
        :return: None
        """
        raise NotImplementedError()

    def add_user(self, user):
        """
        This method append user in users list
        :param user: added user
        :return: None
        """
        raise NotImplementedError()