"""This module contains class Database - base class for all type of database"""


class Database:
    """"""
    def __init__(self, filename, cls_seq=None):
        self.cls_seq = cls_seq
        self.filename = filename

    def load(self):
        """
        This method load data from storage
        :return: instance from storage
        """
        pass

    def unload(self, instance):
        """
        This method unload data to storage
        :param instance: instance to unload
        :return: None
        """
        pass
