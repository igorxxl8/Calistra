"""This module contains all important program constants"""

from datetime import timedelta
from datetime import datetime
import calendar
import os


class Files:
    FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
    TASKS_FILE = os.path.join(FOLDER, 'tasks.json')
    PLANS_FILE = os.path.join(FOLDER, 'plans.json')
    QUEUES_FILE = os.path.join(FOLDER, 'queues.json')
    USERS_FILE = os.path.join(FOLDER, 'users.json')
    AUTH_FILE = os.path.join(FOLDER, 'auth.json')
    ONLINE = os.path.join(FOLDER, 'online_user.json')
    LOG_FILE = os.path.join(FOLDER, 'logs.log')
    LOG_CONFIG = os.path.join(FOLDER, 'logger.config')
    FILES = [
        (TASKS_FILE, '[]'),
        (QUEUES_FILE, '[]'),
        (PLANS_FILE, '[]'),
        (USERS_FILE, '[]'),
        (AUTH_FILE, '[]'),
        (ONLINE, '""'),
        (LOG_FILE, '')
    ]


class LoggingConstants:
    LOG_FILE = os.path.join(Files.FOLDER, 'logs.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Constants:
    """Class for special constants booked by program"""
    DEFAULT_QUEUE = 'default'
    UNDEFINED = '?'


class PlanPeriod:
    """Class whick represent period param of plan"""
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


def get_year_days_num():
    """
    This function calculate number of days in year
    :return: number of days in year
    """
    year = datetime.now().year
    if year % 4 == 0:
        if year % 100 == 0 and year % 400 != 0:
            return 365
        return 366
    return 365


class Time:
    """

    """
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
