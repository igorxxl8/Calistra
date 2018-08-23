try:
    from lib.calistra_lib.constants import Time
    from lib.calistra_lib.exceptions.plan_exceptions import PlanNotFoundError
    from lib.calistra_lib.plan.plan_storage import PlanStorage
    from lib.calistra_lib.task.task import Task
    from lib.calistra_lib.plan.plan import Plan

except ImportError:
    from calistra_lib.constants import Time
    from calistra_lib.exceptions.plan_exceptions import PlanNotFoundError
    from calistra_lib.plan.plan_storage import PlanStorage
    from calistra_lib.task.task import Task
    from calistra_lib.plan.plan import Plan


class PlanController:
    def __init__(self, plan_storage: PlanStorage):
        self.plans_storage = plan_storage

    def create_plan(self, key, author, name, period, activation_time, reminder):
        plan = Plan(key, author.nick, name, period, activation_time, reminder)
        self.plans_storage.add_plan(plan)
        self.plans_storage.save_plans()
        return plan

    def edit_plan(self, key, new_name, period, time, reminder):
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
        plan = self.plans_storage.get_plan_by_key(key)
        if plan is None:
            raise PlanNotFoundError('key - {}'.format(key))
        self.plans_storage.remove_plan(plan)
        self.plans_storage.save_plans()
        return plan

    def get_user_plans(self, user):
        plans = []
        for plan in self.plans_storage.plans:
            if plan.author == user.nick:
                plans.append(plan)

        return plans

    def update_all_plans(self):
        planned_tasks = []
        for plan in self.plans_storage.plans:
            if Time.NOW >= Time.get_date(plan.time):
                time_diff = Time.NOW - Time.get_date(plan.time)
                interval = Time.Interval[plan.period]
                if time_diff < Time.DELTA:
                    planned_tasks.append(self.make_plan_task(plan))
                    next_time_activation = Time.get_date_string(
                        Time.get_date(plan.time) + interval
                    )
                    plan.time = next_time_activation
        self.plans_storage.save_plans()
        return planned_tasks

    @staticmethod
    def make_plan_task(plan):
        start = Time.get_date_string(Time.NOW)
        deadline = Time.get_date_string(Time.NOW + Time.Interval[plan.period])
        return Task(key=plan.key, name=plan.name, reminder=plan.reminder,
                    author=plan.author, start=start, deadline=deadline,
                    creating_time=start)
