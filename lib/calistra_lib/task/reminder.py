"""This module contains class Reminder and other help classes for working
with task reminder mechanism"""


from collections import namedtuple
from calistra_lib.constants import Time
from calistra_lib.messages import Messages


class Frequency:
    """Constants for reminder frequency"""
    EVERY_WEEK = 'every_week'
    EVERY_DAY = 'every_day'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'


class Reminder:
    """
    Class for checking reminder format and terms of it executing
    """
    Reminder = namedtuple('Reminder', ['task', 'messages'])

    @staticmethod
    def check_format(reminder):
        """
        Method which check reminder format correctness and correct it if
         possible
        :param reminder:
        :raise ValueError
        :return:

        """
        if reminder is None:
            return None

        reminder = reminder.split(':')
        if len(reminder) != 2:
            return False
        frequency = list(set(reminder[0].split(',')))

        # delete repeating elements
        times = list(set(reminder[1].split(',')))
        try:
            for item in frequency:
                # check that frequency item is available value
                if item not in Frequency.__dict__.values():
                    return False
                if item == Frequency.EVERY_DAY or item == Frequency.EVERY_WEEK:
                    if len(frequency) != 1:
                        return False

            for time in times:
                Time.get_time(time)
        except ValueError:
            return False

        # reminder without repeating elements in correct format
        corrected_reminder = ':'.join([','.join(frequency), ','.join(times)])

        return corrected_reminder

    @staticmethod
    def check_auto_reminder(task):
        """
        This method check reminders which notify user an day, 2 hour
        and hour before the start about necessary to perform task
        :param task: task with reminder for checking
        :return: messages
        """
        # auto reminder - reminders which notify user in define by program time
        # this function collect all messages about necessary to notify user
        messages = []
        if task.start:
            start = Time.get_date(task.start)
            time_diff = start - Time.NOW
            # check that the task start time is in an hour
            if Time.ZERO < time_diff < Time.HOUR:
                messages.append(Messages.TASK_START_IN_A_HOUR.format(
                    task.name, task.key, start.time())
                )

            # check that the task start time is in an two hour and more
            # than hour
            elif Time.HOUR < time_diff < Time.TWO_HOURS:
                messages.append(Messages.TASK_START_IN_TWO_HOURS.format(
                    task.name, task.key, start.time())
                )

            # check that the task start time is in a day
            elif (time_diff < Time.DAY
                  and start.day != Time.NOW.day):
                messages.append(Messages.TASK_START_TOMORROW.format(
                    task.name, task.key, start.time()
                ))

        if task.deadline:
            deadline = Time.get_date(task.deadline)
            time_diff = deadline - Time.NOW
            # check that the task deadline time is in an hour
            if Time.ZERO < time_diff < Time.HOUR:
                messages.append(Messages.TASK_DEADLINE_IN_A_HOUR.format(
                    task.name, task.key, deadline.time())
                )

            # check that the task deadline time is in an two hour
            elif Time.HOUR < time_diff < Time.TWO_HOURS:
                messages.append(Messages.TASK_DEADLINE_IN_TWO_HOURS.format(
                    task.name, task.key, deadline.time())
                )

            # check that the task deadline time is in a day
            elif (time_diff < Time.DAY
                  and deadline.day != Time.NOW.day):
                messages.append(Messages.TASK_DEADLINE_TOMORROW.format(
                    task.name, task.key, deadline.time()))

        return messages

    @staticmethod
    def check_reminder_time(task):
        """
        This method usign for check tasks for availability of necessary
         to notiry user
        :param task: task with reminder for checking
        :return: messages
        """
        messeges = []
        reminder = task.reminder.split(':')
        frequency = list(set(reminder[0].split(',')))
        times = list(set(reminder[1].split(',')))

        # check that period is every day or today is defined by user day of
        # week to remind user
        if (Frequency.EVERY_DAY in frequency or
                Time.get_day_name(Time.NOW) in frequency):

            for time in times:
                # check that the reminder time has come
                reminder_time = Time.get_time(time).time()
                # lower and upper bound - intervals for checking reminder time
                lower_bound = (Time.NOW - Time.DELTA).time()
                upper_bound = (Time.NOW + Time.DELTA).time()
                if lower_bound < reminder_time < upper_bound:
                    messeges.append(Messages.TASK_REMINDER.format(
                        task.name, task.key, time)
                    )

        return messeges
