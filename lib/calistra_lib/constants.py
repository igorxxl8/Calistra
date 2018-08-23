from datetime import timedelta
from datetime import datetime
import calendar


class Constants:
    DEFAULT_QUEUE = 'default'
    UNDEFINED = '?'


class PlanPeriod:
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


def get_year_days_num():
    year = datetime.now().year
    if year % 4 == 0:
        if year % 100 == 0 and year % 400 != 0:
            return 365
        return 366
    return 365


class Time:
    NOW = datetime.now()

    YEAR = timedelta(days=get_year_days_num())
    MONTH = calendar.mdays[NOW.month]
    WEEK = timedelta(days=7)
    DAY = timedelta(days=1)

    HOUR = timedelta(hours=1)
    TWO_HOURS = timedelta(hours=2)
    DELTA = timedelta(minutes=15)
    ZERO = timedelta(hours=0, days=0)

    SHORT_TIME_FORMAT = '%H.%M'
    DATETIME_FORMAT = '%d.%m.%Y.%H:%M'
    EXTENDED_TIME_FORMAT = '%d.%m.%Y.%H:%M:%S'

    Interval = {
        PlanPeriod.DAILY: DAY,
        PlanPeriod.WEEKLY: WEEK,
        PlanPeriod.MONTHLY: MONTH,
        PlanPeriod.YEARLY: YEAR
    }

    @staticmethod
    def get_time(string):
        return datetime.strptime(string, Time.SHORT_TIME_FORMAT)

    @staticmethod
    def get_date(string):
        return datetime.strptime(string, Time.DATETIME_FORMAT)

    @staticmethod
    def get_date_string(date):
        return date.strftime(Time.DATETIME_FORMAT)

    @staticmethod
    def get_day_name(date: datetime):
        return calendar.day_name[date.weekday()].lower()
