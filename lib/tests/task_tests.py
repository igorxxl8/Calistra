from datetime import datetime as dt
from unittest import TestCase
from calistra_lib.task.reminder import Reminder
from calistra_lib.constants import Time
from calistra_lib.task.task import Task
from calistra_lib.user.user import User
from calistra_lib.queue.queue import Queue
from calistra_lib.task.task_controller import TaskController
from calistra_lib.task.task_storage_interface import ITaskStorage
from calistra_lib.exceptions.task_exceptions import *
from calistra_lib.exceptions.access_exceptions import AccessDeniedError


class TestTaskStorage(ITaskStorage):
    def __init__(self):
        self.tasks = []

    def remove_task(self, task):
        self.tasks.remove(task)

    def get_sub_tasks(self, task):
        sub_tasks = []
        for sub_task_key in task.sub_tasks:
            sub_task = self.get_task_by_key(sub_task_key)
            sub_tasks.append(sub_task)
        return sub_tasks

    def get_task_by_key(self, key):
        for task in self.tasks:
            if task.key == key:
                return task

    def get_task_by_name(self, name):
        tasks = []
        for task in self.tasks:
            if task.name == name or task.name.startswith(name):
                tasks.append(task)
        return tasks

    def get_task_by_tag(self, tag):
        tasks = []
        for task in self.tasks:
            if task.tags and tag in task.tags:
                tasks.append(task)
        return tasks

    def save_tasks(self):
        pass

    def add_task(self, task):
        self.tasks.append(task)


class TaskTests(TestCase):

    def setUp(self):
        self.storage = TestTaskStorage()
        self.controller = TaskController(self.storage)
        self.author = User('tester', 0)
        self.responsible = User('resp', 1)
        self.queue = Queue('test', '-1', self.author)
        self.author.queues.append(self.queue)
        self.test_task = Task('My task', key='12345',
                              responsible=[self.responsible.nick],
                              author=self.author.nick, queue=self.queue.key)

        self.parent_task = Task('Parent', key='p1', author=self.author.nick,
                                queue=self.queue.key)

        self.controller_task = Task('controller', key='c1',
                                    author=self.author.nick,
                                    queue=self.queue.key)

        self.storage.tasks.append(self.controller_task)
        self.storage.tasks.append(self.test_task)
        self.storage.tasks.append(self.parent_task)

    def tearDown(self):
        self.storage = None
        self.controller = None
        self.author = None
        self.responsible = None
        self.queue = None
        self.test_task = None
        self.parent_task = None
        self.controller_task = None

    # tests for task controller
    def test_add_simple_task(self):
        task = self.controller.add_task(
            name=self.test_task.name,
            key=self.test_task.key,
            author=self.author,
            queue=self.queue
        )
        self.assertIn(task, self.storage.tasks)

    def test_edit_task(self):
        actual = self.controller.edit_task(task=self.test_task,
                                           name='Edited task',
                                           task_queue=self.queue,
                                           editor=self.author)

        expected = Task(name='Edited task', key='12345', author='tester',
                        queue='-1', responsible=['resp'])
        self.assertEqual(actual.__dict__, expected.__dict__)

    def test_add_sub_task(self):
        sub_task = self.controller.add_task(
            name='My sub task',
            key='354',
            author=self.author,
            queue=self.queue,
            parent='p1'
        )
        self.assertIn(sub_task.key, self.parent_task.sub_tasks)

    def test_remove_task(self):
        self.task_for_remove = Task('reM_TASK', key='3456',
                                    author=self.author.nick,
                                    queue=self.queue.key)
        self.storage.tasks.append(self.task_for_remove)

        self.controller.remove_task(self.task_for_remove, self.author, True)
        self.assertNotIn(self.task_for_remove, self.storage.tasks)

    def test_try_unrec_remove_tasks_with_sub_tasks(self):
        self.controller.add_task(author=self.author, name='sub task',
                                 key='6543', queue=self.queue, parent='p1')
        with self.assertRaises(DeletingTaskError):
            self.controller.remove_task(self.parent_task, self.author)

    def test_remove_task_with_sub_tasks(self):
        task = self.controller.add_task(author=self.author, name='sub task',
                                        key='6543', queue=self.queue,
                                        parent='p1')
        self.controller.remove_task(self.parent_task, self.author, True)
        self.assertNotIn(self.parent_task, self.storage.tasks)
        self.assertNotIn(task, self.storage.tasks)

    def test_try_to_remove_task_by_responsible_user(self):
        task = self.controller.add_task(author=self.author, name='task',
                                        key='6543', queue=self.queue,
                                        responsible=self.responsible.nick)
        with self.assertRaises(AccessDeniedError):
            self.controller.remove_task(task, self.responsible, True)

    def test_try_to_remove_task_by_unknown_user(self):
        unknown = User('unknown', 32)
        task = self.controller.add_task(author=self.author, name='task',
                                        key='654433', queue=self.queue)
        with self.assertRaises(AccessDeniedError):
            self.controller.remove_task(task, unknown, True)

    def test_try_to_edit_task_by_unknown_user(self):
        user = User('unknown', 2)
        with self.assertRaises(AccessDeniedError):
            self.controller.edit_task(self.test_task, self.queue, user,
                                      name='New name')

    def test_try_to_edit_task_params_by_responsible_user(self):
        """
        This method test case when responsible user try to edit task params
        besides status and progress
        :raise: AccessDeniedError
        :return: None
        """
        with self.assertRaises(AccessDeniedError):
            self.controller.edit_task(self.test_task, self.queue,
                                      self.responsible, name='New name')

    def test_edit_task_by_responsible_user_without_activation(self):
        """
        :raise: AccessDeniedError
        :return: None
        """
        with self.assertRaises(AccessDeniedError):
            self.controller.edit_task(self.test_task, task_queue=self.queue,
                                      editor=self.responsible, progress=50,
                                      status='solved')

    def test_edit_task_status_and_progress_by_responsible(self):
        """
        :raise: AccessDeniedError
        :return: None
        """
        self.responsible.tasks_responsible.append(self.test_task.key)
        self.controller.edit_task(self.test_task, task_queue=self.queue,
                                  editor=self.responsible, progress=50,
                                  status='solved')

    def test_edit_deadline(self):
        deadline = '30.09.2018.9:00'
        self.controller.edit_deadline(self.test_task, deadline)
        self.assertEqual(self.test_task.deadline, '30.09.2018.9:00')

    def test_edit_deadline_throws_error(self):
        deadline = '30.08.2018.9:00'
        with self.assertRaises(TaskDeadlineError):
            self.controller.edit_deadline(self.test_task, deadline)

    def test_edit_deadline_earlier_than_start(self):
        self.test_task.start = '25.10.2018.9:00'
        deadline = '23.10.2018.9:00'
        with self.assertRaises(TaskDeadlineError):
            self.controller.edit_deadline(self.test_task, deadline)

    def test_try_to_set_status_solved_when_task_failed(self):
        self.test_task.status = 'failed'
        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(self.test_task, 'solved')

    def test_try_to_set_status_opened_when_task_failed_with_deadline(self):
        task = self.controller.add_task(author=self.author,
                                        name='task failed',
                                        key='6543gd', queue=self.queue,
                                        deadline='30.08.2018.9:00')
        task.status = 'failed'
        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(task, 'opened')

    def test_try_to_set_status_solved_for_task_with_opened_sub_tasks(self):
        parent_task = self.controller.add_task(author=self.author,
                                               name='parent task',
                                               key='6543gd', queue=self.queue)
        self.controller.add_task(author=self.author,
                                 name='sub task', parent='6543gd',
                                 key='654gghdd', queue=self.queue)
        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(parent_task, 'solved')

    def test_try_to_set_status_opened_for_task_with_failed_sub_tasks(self):
        parent_task = self.controller.add_task(author=self.author,
                                               name='parent task',
                                               key='6543gd', queue=self.queue)
        sub_task = self.controller.add_task(author=self.author,
                                            name='sub task', parent='6543gd',
                                            key='654gghdd', queue=self.queue)
        sub_task.status = 'failed'
        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(parent_task, 'solved')

    def test_try_to_edit_status_for_task_with_controller(self):
        task = self.controller.add_task(author=self.author,
                                        name='task with controller',
                                        key='6543gd', queue=self.queue,
                                        related='c1:controller')

        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(task, 'solved')

    def test_is_task_has_unsolved_blockers(self):
        self.controller.add_task(author=self.author,
                                 name='blocker_1',
                                 key='b1', queue=self.queue)
        self.controller.add_task(author=self.author,
                                 name='blocker_2',
                                 key='b2', queue=self.queue)
        task = self.controller.add_task(author=self.author,
                                        name='task with blockers',
                                        key='mb2', queue=self.queue,
                                        related='b1,b2:blocker')
        self.assertTrue(self.controller.is_task_has_unsolved_blockers(task))

    def test_try_to_solve_task_with_unsolved_blockers(self):
        blocker1 = self.controller.add_task(author=self.author,
                                            name='blocker_1',
                                            key='b1', queue=self.queue)
        self.controller.add_task(author=self.author,
                                 name='blocker_2',
                                 key='b2', queue=self.queue)
        task = self.controller.add_task(author=self.author,
                                        name='task with blockers',
                                        key='mb2', queue=self.queue,
                                        related='b1,b2:blocker')
        blocker1.status = 'solved'

        with self.assertRaises(TaskStatusError):
            self.controller.edit_status(task, 'solved')

    def test_is_task_has_solved_blockers(self):
        blocker1 = self.controller.add_task(author=self.author,
                                            name='blocker_1',
                                            key='b1', queue=self.queue)
        blocker2 = self.controller.add_task(author=self.author,
                                            name='blocker_2',
                                            key='b2', queue=self.queue)
        task = self.controller.add_task(author=self.author,
                                        name='task with blockers',
                                        key='mb2', queue=self.queue,
                                        related='b1,b2:blocker')
        blocker1.status = 'solved'
        blocker2.status = 'solved'
        self.assertFalse(self.controller.is_task_has_unsolved_blockers(task))

    def test_check_controller_task_work(self):
        task = self.controller.add_task(author=self.author,
                                        name='task with controller',
                                        key='6543gd', queue=self.queue,
                                        related='c1:controller')
        self.controller_task.status = 'failed'
        self.controller.update_all()
        self.assertEqual(task.status, 'failed')

    def test_check_reminders(self):
        task = self.controller.add_task(author=self.author,
                                        name='task with reminder',
                                        key='11', queue=self.queue,
                                        reminder='every_day:9.00')

        Time.NOW = dt(2018, 1, 9, 9, 0)
        _, __, ___, notified = self.controller.update_all()

        expected_reminder = Reminder.Reminder(
            task=task,
            messages=[
                'REMINDER: You have task '
                '"task with reminder"(11). It\'s'
                ' good time to do it - 9.00 '
            ]
        )

        self.assertIn(expected_reminder, notified)

    def test_find_task_by_key(self):
        task = self.controller.add_task(author=self.author,
                                        name='task',
                                        key='11', queue=self.queue,
                                        reminder='every_day:9.00')

        expected_task = self.controller.find_task(key='11')
        self.assertEqual(task, expected_task)

    def test_find_tasks_by_name(self):
        task1 = self.controller.add_task(author=self.author,
                                         name='task 1',
                                         key='13253', queue=self.queue,
                                         reminder='every_day:9.00')

        task2 = self.controller.add_task(author=self.author,
                                         name='task 2',
                                         key='13dsf53', queue=self.queue,
                                         reminder='every_day:9.00')

        task3 = self.controller.add_task(author=self.author,
                                         name='not in found task 13',
                                         key='1325sdf3', queue=self.queue,
                                         reminder='every_day:9.00')

        expected_tasks = self.controller.find_task(name='task')
        self.assertListEqual([task1, task2], expected_tasks)

    def test_find_task_by_tag(self):
        task1 = self.controller.add_task(author=self.author,
                                         name='task 1',
                                         key='13253', queue=self.queue,
                                         reminder='every_day:9.00',
                                         tags='super,chetko')

        task2 = self.controller.add_task(author=self.author,
                                         name='task 2',
                                         key='13dsf53', queue=self.queue,
                                         reminder='every_day:9.00',
                                         tags='vasya,super')

        task3 = self.controller.add_task(author=self.author,
                                         name='noin found task 13',
                                         key='1325sdf3', queue=self.queue,
                                         reminder='every_day:9.00',
                                         tags='tinder,reminder')

        task4 = self.controller.add_task(author=self.author,
                                         name='not task 65',
                                         key='1325sdf3', queue=self.queue,
                                         reminder='every_day:9.00',
                                         tags='tinder,reminder,super')

        expected_tasks = self.controller.find_task(tag='super')
        self.assertListEqual([task1, task2, task4], expected_tasks)


