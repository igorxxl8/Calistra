"""This module contains class IPlanStorage - basic class for different types
 of plans storage databases"""


class IPlanStorage:
    """This class represent basic interface for implementing classes for plan
     storage instances"""
    def __init__(self, plans):
        self.plans = plans

    def add_plan(self, plan):
        """
        This method add plan in plan storage
        :param plan: added plan
        :return: None
        """
        raise NotImplementedError()

    def remove_plan(self, plan):
        """
        This method remove plan from plan storage
        :param plan:
        :return: None
        """
        raise NotImplementedError()

    def save_plans(self):
        """
        This method unload plans in database
        :return: None
        """
        raise NotImplementedError()

    def get_plan_by_key(self, key):
        """
        This method find in plan storage plan by key
        :param key: plan access key
        :return: queried plan
        """
        raise NotImplementedError()