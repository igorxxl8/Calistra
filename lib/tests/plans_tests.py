from datetime import datetime as dt
from unittest import TestCase
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.plan.plan import Plan
from calistra_lib.plan.plan_storage_interface import IPlanStorage
from calistra_lib.user.user import User
from calistra_lib.task.task import Task
from calistra_lib.constants import Time


class TestPlanStorage(IPlanStorage):
    def add_plan(self, plan):
        self.plans.append(plan)

    def remove_plan(self, plan):
        self.plans.remove(plan)

    def save_plans(self):
        pass

    def get_plan_by_key(self, key):
        for plan in self.plans:
            if plan.key == key:
                return plan


class PlanTests(TestCase):
    def setUp(self):
        self.storage = TestPlanStorage([])
        self.controller = PlanController(self.storage)
        self.author = User('tester', 0)

    def tearDown(self):
        self.storage = None
        self.controller = None
        self.author = None

    def test_add_simple_plan(self):
        plan = self.controller.create_plan(
            key='1',
            author=self.author,
            name='Test plan',
            period='daily',
            activation_time='20.09.2018.9:00'
        )
        self.assertIn(plan, self.storage.plans)

    def test_edit_plan(self):
        self.controller.create_plan(
            key='1',
            author=self.author,
            name='Test plan',
            period='daily',
            activation_time='20.09.2018.9:00'
        )
        actual = self.controller.edit_plan(key='1', new_name='Edited plan',
                                           period='monthly',
                                           time='21.09.2018.9:00')

        expected = Plan(
            key='1',
            author=self.author.nick,
            name='Edited plan',
            period='monthly',
            activation_time='21.09.2018.9:00',
            reminder=None
        )
        self.assertEqual(actual.__dict__, expected.__dict__)

    def test_delete_plan(self):
        self.controller.create_plan(
            key='2',
            author=self.author,
            name='plan to delete',
            period='daily',
            activation_time='20.09.2018.9:00'
        )
        deleted_plan = self.controller.delete_plan('2')
        self.assertNotIn(deleted_plan, self.storage.plans)

    def get_user_plans(self):
        plan_1 = self.controller.create_plan(
            key='1',
            author=self.author,
            name='plan 1',
            period='daily',
            activation_time='20.09.2018.9:00'
        )

        plan_2 = self.controller.create_plan(
            key='2',
            author=self.author,
            name='plan 2',
            period='daily',
            activation_time='20.09.2018.9:00'
        )

        plan_3 = self.controller.create_plan(
            key='plan 3',
            author=self.author,
            name='plan 3',
            period='daily',
            activation_time='20.09.2018.9:00'
        )

        plan_4 = self.controller.create_plan(
            key='plan4 ',
            author=User('another user', 0),
            name='plan to delete',
            period='daily',
            activation_time='20.09.2018.9:00'
        )
        actual = self.controller.get_user_plans(self.author)

        self.assertListEqual([plan_1, plan_2, plan_4], actual)

    def test_make_plan_task(self):
        plan = self.controller.create_plan(
            key='1',
            author=self.author,
            name='plan for create task',
            period='daily',
            activation_time='20.09.2018.9:00'
        )
        Time.NOW = dt(2018, 9, 1, 9, 0)
        actual = self.controller.make_plan_task(plan)
        expected = Task(key='1', name='plan for create task', reminder=None,
                        author='tester', start='01.09.2018.09:00',
                        deadline='02.09.2018.09:00',
                        creating_time='01.09.2018.09:00')
        self.assertEqual(actual.__dict__, expected.__dict__)

    def test_planned_tasks(self):
        self.controller.create_plan(
            key='1',
            author=self.author,
            name='test plan',
            period='monthly',
            activation_time='20.09.2018.9:00'
        )
        Time.NOW = dt(2018, 9, 20, 9, 0)
        planned_tasks = self.controller.update_all_plans()
        expected_task = Task(key='1', name='test plan', reminder=None,
                             author='tester', start='20.09.2018.09:00',
                             deadline='20.10.2018.09:00',
                             creating_time='20.09.2018.09:00')
        self.assertDictEqual(expected_task.__dict__, planned_tasks[0].__dict__)


