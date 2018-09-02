"""This module contains all important program constants"""

from datetime import timedelta
from datetime import datetime
import calendar


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
    This class contains time constants
    """
    NOW = datetime.now()

    YEAR = timedelta(days=get_year_days_num())
    MONTH = timedelta(calendar.mdays[NOW.month])
    WEEK = timedelta(days=7)
    DAY = timedelta(days=1)

    HOUR = timedelta(hours=1)
    TWO_HOURS = timedelta(hours=2)

    # DELTA - time interval during which the task time attributes
    # check is performed
    DELTA = timedelta(minutes=15)
    ZERO = timedelta(hours=0, days=0)

    SHORT_TIME_FORMAT = '%H.%M'
    DATETIME_FORMAT = '%d.%m.%Y.%H:%M'
    EXTENDED_TIME_FORMAT = '%d.%m.%Y.%H:%M:%S'

    # dictionary which puts in conformity task frequency and time interval
    Interval = {
        PlanPeriod.DAILY: DAY,
        PlanPeriod.WEEKLY: WEEK,
        PlanPeriod.MONTHLY: MONTH,
        PlanPeriod.YEARLY: YEAR
    }

    @staticmethod
    def get_time(string):
        """
        This method parse string into time object
        :param string: string in time format
        :return: time
        """
        return datetime.strptime(string, Time.SHORT_TIME_FORMAT)

    @staticmethod
    def get_date(string):
        """
        This method parse string into datetime object
        :param string: string in datetime format
        :return: datetime
        """
        return datetime.strptime(string, Time.DATETIME_FORMAT)

    @staticmethod
    def get_date_string(date):
        """
        This method parse datetime object in formatted string
        :param date: date for parsing
        :return: formatted string
        """
        return date.strftime(Time.DATETIME_FORMAT)

    @staticmethod
    def get_day_name(date: datetime):
        """
        This method for getting day of week name
        :param date:
        :return: string
        """
        return calendar.day_name[date.weekday()].lower()
