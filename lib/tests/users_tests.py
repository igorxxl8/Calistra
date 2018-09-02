from unittest import TestCase
from calistra_lib.user.user_storage_interface import IUserStorage
from calistra_lib.user.user_controller import UserController
from calistra_lib.queue.queue import Queue
from calistra_lib.task.task import Task
from calistra_lib.constants import Time
from datetime import datetime as dt


class TestUserStorage(IUserStorage):

    def get_user_by_nick(self, nick):
        for user in self.users:
            if user.nick == nick:
                return user

    def get_user_by_uid(self, uid):
        for user in self.users:
            if user.uid == uid:
                return user

    def save_users(self):
        pass

    def add_user(self, user):
        self.users.append(user)


class UserTests(TestCase):
    def setUp(self):
        self.storage = TestUserStorage([])
        self.controller = UserController(self.storage)

    def test_add_user(self):
        user = self.controller.add_user(nick='tester', uid=0)
        self.assertIn(user, self.storage.users)

    def test_find_user_by_nick(self):
        user_1 = self.controller.add_user(nick='user 1', uid=0)
        igor = self.controller.add_user(nick='igor', uid=1)
        vanya = self.controller.add_user(nick='vanya', uid=2)
        found = self.controller.find_user(nick='igor')
        self.assertEqual(igor, found)

    def test_find_user_by_uid(self):
        user_1 = self.controller.add_user(nick='user 1', uid=0)
        igor = self.controller.add_user(nick='igor', uid=1)
        vanya = self.controller.add_user(nick='vanya', uid=2)
        found = self.controller.find_user(uid=2)
        self.assertEqual(vanya, found)

    def test_clear_user_notifications(self):
        user = self.controller.add_user(nick='tester', uid=0)
        user.notifications.append('Hello')
        user.notifications.append('I need to work')
        user.notifications.append('Go home')
        self.controller.clear_user_notifications(user)
        self.assertListEqual(user.notifications, [])

    def test_clear_user_2_old_notifications(self):
        user = self.controller.add_user(nick='tester', uid=0)
        user.notifications.append('Hello')
        user.notifications.append('I need to work')
        user.notifications.append('Go home')
        self.controller.clear_user_notifications(user, 2)
        self.assertListEqual(user.notifications, ['Go home'])

    def test_clear_new_messages(self):
        user = self.controller.add_user(nick='tester', uid=0)
        user.notifications.append('other notification')
        user.new_messages.append('1 new notify')
        user.new_messages.append('2 new notify')
        self.controller.clear_new_messages(user)
        self.assertListEqual(user.notifications, ['other notification',
                                                  '1 new notify',
                                                  '2 new notify'])
        self.assertListEqual(user.new_messages, [])

    def test_notify_user(self):
        user = self.controller.add_user(nick='tester', uid=0)
        self.controller.notify_user(user, 'privet', show_time=False)

        self.controller.notify_user(user, 'with time')
        expected_str = ''.join([dt.now().strftime(Time.EXTENDED_TIME_FORMAT),
                                ': ', 'with time'])
        self.assertListEqual(user.new_messages, ['privet', expected_str])

    def test_link_user_with_queue(self):
        user = self.controller.add_user(nick='tester', uid=0)
        queue = Queue('test queue', key='0', owner=user.nick)
        self.controller.link_user_with_queue(user, queue)
        self.assertListEqual(user.queues, ['0'])

    def test_unlink_user_with_queue(self):
        user = self.controller.add_user(nick='tester', uid=0)
        queue = Queue('test queue', key='0', owner=user.nick)
        self.controller.link_user_with_queue(user, queue)
        self.controller.unlink_user_and_queue(user, queue)
        self.assertListEqual(user.queues, [])

    def test_link_responsible_with_task(self):
        owner = self.controller.add_user(nick='owner', uid=0)
        responsible = self.controller.add_user(nick='responsible', uid=1)
        task = Task(name='Test task', key='3453', author=owner.nick)
        self.controller.link_responsible_with_task(responsible, task)
        self.assertListEqual(responsible.tasks_responsible, ['3453'])

    def test_unlink_responsible_with_task(self):
        owner = self.controller.add_user(nick='owner', uid=0)
        responsible = self.controller.add_user(nick='responsible', uid=1)
        task = Task(name='Test task', key='3453', author=owner.nick)
        self.controller.link_responsible_with_task(responsible, task)
        self.controller.unlink_responsible_and_task(responsible, task)
        self.assertListEqual(responsible.tasks_responsible, [])

    def test_link_author_with_task(self):
        owner = self.controller.add_user(nick='owner', uid=0)
        task = Task(name='Test task', key='3453', author=owner.nick)
        self.controller.link_author_with_task(owner, task)
        self.assertListEqual(owner.tasks_author, ['3453'])

    def test_unlink_author_with_task(self):
        owner = self.controller.add_user(nick='owner', uid=0)
        task = Task(name='Test task', key='3453', author=owner.nick)
        self.controller.link_author_with_task(owner, task)
        self.controller.unlink_author_and_task(owner, task)
        self.assertListEqual(owner.tasks_author, [])


