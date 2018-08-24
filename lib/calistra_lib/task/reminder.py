from collections import namedtuple
from calistra_lib.constants import Time
from calistra_lib.messages import Messages


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
                Time.get_time(time)
        except ValueError:
            return False

        corrected_reminder = ':'.join([','.join(frequency), ','.join(times)])

        return corrected_reminder

    @staticmethod
    def check_auto_reminder(task):
        # TODO: отредактировать чтобы не показывалось постоянно
        messages = []
        if task.start:
            start = Time.get_date(task.start)
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
            deadline = Time.get_date(task.deadline)
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
                messages.append(Messages.TASK_DEADLINE_TOMORROW.format(
                    task.name, task.key, deadline.time()))

        return messages

    @staticmethod
    def check_reminder_time(task):
        # TODO: отредактировать чтобы не показывалось постоянно
        # и тестировать
        messeges = []
        reminder = task.reminder.split(':')
        frequency = list(set(reminder[0].split(',')))
        times = list(set(reminder[1].split(',')))

        if (Frequency.EVERY_DAY in frequency or
                Time.get_day_name(Time.NOW) in frequency):

            for time in times:
                reminder_time = Time.get_time(time).time()
                lower_bound = (Time.NOW - Time.DELTA).time()
                upper_bound = (Time.NOW + Time.DELTA).time()
                if lower_bound < reminder_time < upper_bound:
                    messeges.append(Messages.TASK_REMINDER.format(
                        task.name, task.key, time)
                    )

        return messeges
