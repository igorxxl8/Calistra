"""
This module contains PlanStorage class which using for store plans
"""

from calistra_lib.plan.plan import Plan
from calistra_lib.storage.json_serializer import JsonDatabase
from calistra_lib.plan.plan_storage_interface import IPlanStorage


class JsonPlanStorage(IPlanStorage):
    """This class implement IPlanStorage interface and represent instance
     which store plans in file in json format"""
    def __init__(self, path_to_plans_file):
        self.plans_db = JsonDatabase(path_to_plans_file, cls_seq=[Plan])
        super().__init__(self.plans_db.load())

    def add_plan(self, plan):
        """
        This method add plan in plan storage
        :param plan: added plan
        :return: None
        """
        self.plans.append(plan)

    def remove_plan(self, plan):
        """
        This method remove plan from plan storage
        :param plan:
        :return: None
        """
        self.plans.remove(plan)

    def save_plans(self):
        """
        This method unload plans in database
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

