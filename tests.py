from unittest import TestCase
from app.help_functions import *


class TestHelpFunctions(TestCase):

    def test_concat(self):
        first = 'Hello'
        second = 'my'
        third = 'friend'
        actual = concat(first, second, third)
        expected = 'Hellomyfriend'
        self.assertEqual(expected, actual)

    def test_get_date(self):
        time_string = '01.09.2018.19:00'
        actual = get_date(time_string)
        expected = dt(2018, 9, 1, 19, 0)
        self.assertEqual(expected, actual)

    def test_check_str_len(self):
        string = 'afdbdberfv'
        actual = check_str_len(string)
        expected = 'afdbdberfv'
        self.assertEqual(expected, actual)

    def test_check_str_len_incorrect(self):
        string = ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        self.assertRaises(ValueError, check_str_len, string)

    def test_check_str_len_incorrect_2(self):
        self.assertRaises(ValueError, check_str_len, '')

    # test methods for function check_priority_correctness
    def test_check_priority_correctness_1(self):
        priority = 'high'
        actual = check_priority_correctness(priority)
        expected = 10
        self.assertEqual(expected, actual)

    def test_check_priority_correctness_2(self):
        priority = 'low'
        actual = check_priority_correctness(priority)
        expected = -10
        self.assertEqual(expected, actual)

    def test_check_priority_correctness_3(self):
        priority = '7'
        actual = check_priority_correctness(priority)
        expected = 7
        self.assertEqual(expected, actual)

    def test_check_priority_incorrectness(self):
        self.assertRaises(ValueError, check_priority_correctness, 'lover')

    def test_check_priority_incorrectness_2(self):
        self.assertRaises(ValueError, check_priority_correctness, '11')

    def test_check_priority_incorrectness_3(self):
        self.assertRaises(ValueError, check_priority_correctness, '-11')

    # test methods for function check_status_correctness
    def test_check_status_correctness(self):
        status = 'solved'
        actual = check_status_correctness(status)
        expected = 'solved'
        self.assertEqual(expected, actual)

    def test_check_status_incorrectness(self):
        self.assertRaises(ValueError, check_status_correctness, 'reshon')

    def test_check_progress_correctness(self):
        progress = '50'
        actual = check_progress_correctness(progress)
        expected = 50
        self.assertEqual(expected, actual)

    def test_check_progress_incorrectness(self):
        self.assertRaises(ValueError, check_progress_correctness, '101')

    def test_check_progress_incorrectness_2(self):
        self.assertRaises(ValueError, check_progress_correctness, '-1')

    def test_check_progress_incorrectness_3(self):
        self.assertRaises(ValueError, check_progress_correctness, 'abc')

    def test_check_time_format(self):
        time_string = '20.08.2018.9:00'
        actual = check_time_format(time_string, '')
        expected = '20.08.2018.9:00'
        self.assertEqual(expected, actual)

    def test_check_time_format_2(self):
        self.assertRaises(ValueError, check_time_format, '21.23.2018.9:01', '')

    def test_check_time_format_3(self):
        self.assertRaises(ValueError, check_time_format, '21:03:2018.9:01', '')

    def test_validate_activation_time(self):
        time = '12.09.2018.10:00'
        actual = validate_activation_time(time)
        expected = None
        self.assertEqual(expected, actual)

    def test_validate_activation_time_2(self):
        time = '1.09.2018.10:00'
        self.assertRaises(ValueError, validate_activation_time, time)

    def test_check_period_format(self):
        period = 'daily'
        actual = check_period_format(period)
        expected = None
        self.assertEqual(expected, actual)

    def test_check_period_format_2(self):
        period = 'testly'
        self.assertRaises(ValueError, check_period_format, period)

    def test_check_terms_correctness(self):
        start = '1.09.2018.9:00'
        deadline = '20.09.2018.9:00'
        actual = check_terms_correctness(start, deadline)
        self.assertEqual(None, actual)

    def test_check_terms_incorrectness(self):
        start = '1.09.2018.9:00'
        deadline = '1.09.2018.8:00'
        self.assertRaises(ValueError, check_terms_correctness, start, deadline)

    def test_check_terms_incorrectness_2(self):
        start = '1.09.2018.9:00'
        deadline = '1.09.2018.18:00'
        self.assertRaises(ValueError, check_terms_correctness, start, deadline)

    def test_check_tags_correctness(self):
        tags = 'super,class,cool'
        actual = check_tags_correctness(tags)
        expected = ['super', 'class', 'cool']
        self.assertEqual(expected, actual)

    def test_check_tags_incorrectness(self):
        tags = 'super,class,,,,,cool'
        self.assertRaises(ValueError, check_tags_correctness, tags)

    def test_check_reminder_format(self):
        reminder = 'every_day:9.00'
        actual = check_reminder_format(reminder, '')
        expected = 'every_day:9.00'
        self.assertEqual(expected, actual)

    def test_check_reminder_format_incorrectness(self):
        reminder = 'every_day:9.00,,,10.00'
        self.assertRaises(ValueError, check_reminder_format, reminder, '')

    def test_check_reminder_format_incorrectness_1(self):
        reminder = 'every:9.00,,,10.00'
        self.assertRaises(ValueError, check_reminder_format, reminder, '')

    def test_check_related_correctness(self):
        related = '43fsags32534:blocker'
        actual = check_related_correctness(related)
        expected = None
        self.assertEqual(expected, actual)

    def test_check_related_incorrectness(self):
        self.assertRaises(ValueError, check_related_correctness, 'fgs::blocker')

    def test_check_related_incorrectness_1(self):
        self.assertRaises(ValueError, check_related_correctness, 'ey453:bloc')

    def test_check_responsible_correctness(self):
        responsible = 'user,user1,user2'
        actual = check_responsible_correctness(responsible)
        expected = ['user', 'user1', 'user2']
        self.assertEqual(expected, actual)

    def test_check_responsible_incorrectness(self):
        test = 'user,user1, , ,user2'
        self.assertRaises(ValueError, check_responsible_correctness, test)
