from datetime import datetime, timedelta
import calendar
from collections import namedtuple

try:
    from lib.calistra_lib.messages import Messages
except ImportError:
    from calistra_lib.messages import Messages


class Time:
    WEEK = timedelta(days=7)
    DAY = timedelta(days=1)
    HOUR = timedelta(hours=1)
    TWO_HOURS = timedelta(hours=2)
    DELTA = timedelta(minutes=15)
    ZERO = timedelta(hours=0, days=0)
    NOW = datetime.now()
    MONTH = calendar.mdays[NOW.month]
    TIME_FORMAT = '%H.%M'
    DATETIME_FORMAT = '%d.%m.%Y.%H:%M'


class Frequency:
    EVERY_WEEK = 'every_week'
    EVERY_DAY = 'every_day'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'


def get_time(string):
    return datetime.strptime(string, Time.TIME_FORMAT)


def get_date(string):
    return datetime.strptime(string, Time.DATETIME_FORMAT)


def get_day_name(date: datetime):
    return calendar.day_name[date.weekday()].lower()


class Reminder:
    Reminder = namedtuple('Reminder', ['task', 'messages'])

    @staticmethod
    def check_format(reminder):
        if reminder is None:
            return None

        reminder = reminder.split(':')
        if len(reminder) != 2:
            return False
        frequency = list(set(reminder[0].split(',')))
        times = list(set(reminder[1].split(',')))
        try:
            for item in frequency:
                if item not in Frequency.__dict__.values():
                    return False
                if item == Frequency.EVERY_DAY or item == Frequency.EVERY_WEEK:
                    if len(frequency) != 1:
                        return False

            for time in times:
                get_time(time)
        except ValueError:
            return False

        corrected_reminder = ':'.join([','.join(frequency), ','.join(times)])

        return corrected_reminder

    @staticmethod
    def check_auto_reminder(task):
        messages = []
        if task.start:
            start = get_date(task.start)
            time_diff = start - Time.NOW
            if Time.ZERO < time_diff < Time.HOUR:
                messages.append(Messages.TASK_START_IN_A_HOUR.format(
                    task.name, task.key, start.time())
                )

            elif Time.HOUR < time_diff < Time.TWO_HOURS:
                messages.append(Messages.TASK_START_IN_TWO_HOURS.format(
                    task.name, task.key, start.time())
                )

            elif (time_diff < Time.DAY
                  and start.day != Time.NOW.day):
                messages.append(Messages.TASK_START_TOMORROW.format(
                    task.name, task.key, start.time()
                ))

        if task.deadline:
            deadline = get_date(task.deadline)
            time_diff = deadline - Time.NOW
            if Time.ZERO < time_diff < Time.HOUR:
                messages.append(Messages.TASK_DEADLINE_IN_A_HOUR.format(
                    task.name, task.key, deadline.time())
                )

            elif Time.HOUR < time_diff < Time.TWO_HOURS:
                messages.append(Messages.TASK_DEADLINE_IN_TWO_HOURS.format(
                    task.name, task.key, deadline.time())
                )

            elif (time_diff < Time.DAY
                  and deadline.day != Time.NOW.day):
                messages.append(Messages.TASK_START_TOMORROW.format(
                    task.name, task.key, deadline.time()))

        return messages

    @staticmethod
    def check_reminder_time(task):
        messeges = []
        reminder = task.reminder.split(':')
        frequency = list(set(reminder[0].split(',')))
        times = list(set(reminder[1].split(',')))
        if Frequency.EVERY_DAY in frequency:
            for time in times:
                if get_time(time) == Time.NOW:
                    messeges.append(Messages.TASK_REMINDER.format(
                        task.name, task.key, time)
                    )
        elif get_day_name(Time.NOW) in frequency:
            for time in times:
                current_time = get_time(time)
                if current_time.hour == Time.NOW.hour:
                    messeges.append(Messages.TASK_REMINDER.format(
                        task.name, task.key, time)
                    )
