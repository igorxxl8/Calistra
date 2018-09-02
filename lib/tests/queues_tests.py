from unittest import TestCase
from calistra_lib.queue.queue import Queue
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.queue.queue_storage_interface import IQueueStorage
from calistra_lib.constants import Constants
from calistra_lib.task.task import Task
from calistra_lib.user.user import User
from calistra_lib.exceptions.queue_exceptions import *
from calistra_lib.exceptions.access_exceptions import AccessDeniedError


class TestQueueStorage(IQueueStorage):

    def save_queues(self):
        pass

    def add_queue(self, queue):
        self.queues.append(queue)

    def remove_queue(self, queue):
        self.queues.remove(queue)

    def get_queue_by_key(self, key):
        for queue in self.queues:  # type: Queue
            if key == queue.key:
                return queue

    def get_queue_by_name(self, name):
        for queue in self.queues:
            if name == queue.name:
                return queue

    def get_user_default_queue(self, user):
        for queue in self.queues:
            if queue.owner == user.uid:
                if queue.name == 'default':
                    return queue


class QueueTests(TestCase):
    def setUp(self):
        self.storage = TestQueueStorage([])
        self.controller = QueueController(self.storage)
        self.owner = User('tester', 0)
        self.default_queue = Queue(key='-100',
                                   name=Constants.DEFAULT_QUEUE,
                                   owner=self.owner.uid)
        self.owner.queues.append(self.default_queue.key)
        self.storage.add_queue(self.default_queue)

    def tearDown(self):
        self.storage = None
        self.controller = None
        self.owner = None
        self.default_queue = None

    def test_add_simple_queue(self):
        queue = self.controller.add_queue(
            key='1', name='test queue', owner=self.owner)

        self.assertIn(queue, self.storage.queues)

    def test_edit_queue(self):
        self.controller.add_queue(key='1', name='test queue', owner=self.owner)
        actual = self.controller.edit_queue(key='1', new_name='edited queue',
                                            editor=self.owner)
        expected = Queue(key='1', name='edited queue', owner=self.owner.uid)
        self.assertDictEqual(actual.__dict__, expected.__dict__)

    def test_try_to_edit_default_queue(self):
        with self.assertRaises(EditingQueueError):
            self.controller.edit_queue(
                key='-100',
                new_name='New name',
                editor=self.owner)

    def test_try_to_edit_queue_by_unknown_user(self):
        self.controller.add_queue(key='54',
                                  name='Queue to edit',
                                  owner=self.owner)

        with self.assertRaises(AccessDeniedError):
            self.controller.edit_queue(
                key='54',
                new_name='new nme',
                editor=User('unknown', -10)
            )

    def test_get_queue_by_key(self):
        expected = self.controller.add_queue(key='54',
                                             name='queue to find',
                                             owner=self.owner)

        actual = self.controller.get_queue_by_key('54')
        self.assertEqual(expected, actual)

    def test_not_found_queue_by_key(self):
        with self.assertRaises(QueueNotFoundError):
            self.controller.get_queue_by_key('55')

    def test_get_user_default_queue(self):
        queue = self.controller.get_user_default_queue(self.owner)
        self.assertEqual(self.default_queue, queue)

    def test_get_user_queues(self):
        queue_1 = self.controller.add_queue(
            key='34',
            name='queue 1',
            owner=self.owner
        )
        self.owner.queues.append('34')
        queue_2 = self.controller.add_queue(
            key='3t43',
            name='queue 2',
            owner=self.owner
        )
        self.owner.queues.append('3t43')
        another_user = User('another user', 32454)
        queue_3 = self.controller.add_queue(
            key='3sg4',
            name='queue 3',
            owner=another_user
        )
        another_user.queues.append('3sg4')
        queue_4 = self.controller.add_queue(
            key='3gfd4ffgd',
            name='queue 4',
            owner=self.owner
        )
        self.owner.queues.append('3gfd4ffgd')

        actual = self.controller.get_user_queues(self.owner)

        expected = [self.default_queue, queue_1, queue_2, queue_4]
        self.assertListEqual(actual, expected)

    def test_link_queue_with_task(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        self.assertIn(task.key, queue.opened_tasks)

    def test_unlink_queue_and_task(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        self.controller.unlink_queue_and_task(queue, task)
        self.assertNotIn(task.key, queue.solved_tasks)
        self.assertNotIn(task.key, queue.opened_tasks)
        self.assertNotIn(task.key, queue.failed_tasks)

    def test_move_in_opened(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        task.status = 'solved'
        queue.solved_tasks.append(task.key)
        self.controller.move_in_opened(queue, task)
        self.assertIn(task.key, queue.opened_tasks)

    def test_move_in_solved(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        task.status = 'solved'
        self.controller.move_in_solved(queue, task)
        self.assertIn(task.key, queue.solved_tasks)

    def test_move_in_failed(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        task.status = 'failed'
        self.controller.move_in_failed(queue, task)
        self.assertIn(task.key, queue.failed_tasks)

    def test_delete_queue(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        self.controller.remove_queue('100', False, self.owner)
        self.assertNotIn(queue, self.storage.queues)

    def test_try_to_unrec_delete_queue_with_tasks(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        with self.assertRaises(DeletingQueueError):
            self.controller.remove_queue('100', False, self.owner)

    def test_rec_delete_queue_with_tasks(self):
        queue = self.controller.add_queue(
            name='Test queue',
            key='100',
            owner=self.owner
        )
        task = Task('test task', key='54354', queue=queue)
        self.controller.link_queue_with_task(queue, task)
        self.controller.remove_queue('100', True, self.owner)
        self.assertNotIn(queue, self.storage.queues)
