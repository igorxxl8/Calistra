"""This module contains PlanController class for working with periodic plans"""

from calistra_lib.constants import Time
from calistra_lib.exceptions.plan_exceptions import PlanNotFoundError
from calistra_lib.plan.plan_storage_interface import IPlanStorage
from calistra_lib.task.task import Task
from calistra_lib.plan.plan import Plan


class PlanController:
    """
    This class describe entity for work with periodic plans.
    """

    def __init__(self, plan_storage: IPlanStorage):
        self.plans_storage = plan_storage

    def create_plan(self, key, author, name, period, activation_time,
                    reminder=None):
        """
        This method create plan
        :param key: plan key
        :param author: plan creator
        :param name: plan name, this name get task too
        :param period: interval of time
        :param activation_time: time when plan create task
        :param reminder: entity which create notification for user about
         necessary to do task
        :return: plan entity
        """
        plan = Plan(key, author.nick, name, period, activation_time, reminder)
        self.plans_storage.add_plan(plan)
        self.plans_storage.save_plans()
        return plan

    def edit_plan(self, key, new_name, period, time, reminder=None):
        """
        This method delete task by key
        :param key: plan key
        :param new_name: new name for plan
        :param period: interval of time
        :param time: time when plan create task
        :param reminder: entity which create notification for user about
         necessary to do task
        :return: edited plan
        """
        plan = self.plans_storage.get_plan_by_key(key)
        if plan is None:
            raise PlanNotFoundError(' key - {}'.format(key))

        if new_name:
            plan.name = new_name

        if period:
            plan.period = period

        if time:
            plan.time = time

        if reminder:
            plan.reminder = reminder

        self.plans_storage.save_plans()
        return plan

    def delete_plan(self, key):
        """
        Delete plan by key
        :param key: plan access key
        :return: deleted plan
        """
        plan = self.plans_storage.get_plan_by_key(key)
        if plan is None:
            raise PlanNotFoundError('key - {}'.format(key))
        self.plans_storage.remove_plan(plan)
        self.plans_storage.save_plans()
        return plan

    def get_user_plans(self, user):
        """
        This module using for getting all user plans
        :param user:
        :return: user plans
        """
        plans = []
        for plan in self.plans_storage.plans:
            if plan.author == user.nick:
                plans.append(plan)

        return plans

    def update_all_plans(self):
        """
        This method check all plans and
        :return: planned tasks
        """
        planned_tasks = []

        # for every plan check it activation and current time
        for plan in self.plans_storage.plans:
            # check that activation time come
            if Time.NOW >= Time.get_date(plan.time):
                time_diff = Time.NOW - Time.get_date(plan.time)
                interval = Time.Interval[plan.period]
                # check that activation time was recently
                # if time_diff < Time.DELTA:
                # add this plan to plans which be activated
                planned_tasks.append(self.make_plan_task(plan))
                # change activation time by adding period time interval
                #  to current activation time
                next_time_activation = Time.get_date_string(
                    Time.get_date(plan.time) + interval)

                plan.time = next_time_activation

        self.plans_storage.save_plans()
        return planned_tasks


    @staticmethod
    def make_plan_task(plan):
        """
        This method using for creating task from plan attributes
        :param plan: plan which create task
        :return: task which create by plan
        """
        start = Time.get_date_string(Time.NOW)
        deadline = Time.get_date_string(Time.NOW + Time.Interval[plan.period])
        return Task(key=plan.key, name=plan.name, reminder=plan.reminder,
                    author=plan.author, start=start, deadline=deadline,
                    creating_time=start)
