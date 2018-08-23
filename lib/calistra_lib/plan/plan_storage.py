try:
    from lib.calistra_lib.plan.plan import Plan
    from lib.calistra_lib.storage.database import Database
except ImportError:
    from calistra_lib.plan.plan import Plan
    from calistra_lib.storage.database import Database


class PlanStorage:
    def __init__(self, plans_db: Database):
        self.plans_db = plans_db
        self.plans = self.plans_db.load()

    def add_plan(self, plan):
        self.plans.append(plan)

    def remove_plan(self, plan):
        self.plans.remove(plan)

    def save_plans(self):
        self.plans_db.unload(self.plans)

    def get_plan_by_key(self, key):
        for plan in self.plans:
            if plan.key == key:
                return plan

