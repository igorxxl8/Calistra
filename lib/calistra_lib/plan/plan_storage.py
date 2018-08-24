"""
This module contains PlanStorage class which using for store plans
"""

from calistra_lib.plan.plan import Plan
from calistra_lib.storage.database import Database


class PlanStorage:
    def __init__(self, plans_db: Database):
        self.plans_db = plans_db
        self.plans = self.plans_db.load()

    def add_plan(self, plan):
        """

        :param plan: added plan
        :return: None
        """
        self.plans.append(plan)

    def remove_plan(self, plan):
        """

        :param plan:
        :return: None
        """
        self.plans.remove(plan)

    def save_plans(self):
        """

        :return: None
        """
        self.plans_db.unload(self.plans)

    def get_plan_by_key(self, key):
        """
        This module find in plan storage task by key
        :param key: plan access key
        :return: queried plan
        """
        for plan in self.plans:
            if plan.key == key:
                return plan

