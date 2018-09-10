from calistra_lib.plan.plan_storage_interface import IPlanStorage
from ..models import Plan


class ORMPlanStorage(IPlanStorage):
    def __init__(self):
        super().__init__(Plan.objects.all())

    def add_plan(self, plan):
        self.plans.create(
            author=plan.author,
            name=plan.name,
            period=plan.period,
            time=plan.time,
            key=plan.key,
            reminder=plan.reminder
        )

    def remove_plan(self, plan):
        self.plans.get(key=plan.key).delete()

    def save_plans(self):
        for plan in self.plans:
            plan.save()

    def get_plan_by_key(self, key):
        try:
            return self.plans.get(key=key)
        except Exception:
            return None

    def get_user_plans(self, user):
        return self.plans.filter(author=user.nick)

