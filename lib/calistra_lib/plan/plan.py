"""This module contains class Plan which describe periodic plans"""


class Plan:
    """This class describe single plan entity"""
    def __init__(self, key, author, name, period, activation_time, reminder=None):

        self.author = author
        self.name = name
        self.period = period
        self.time = activation_time
        self.reminder = reminder
        self.key = key

    def __str__(self):
        time = self.time
        reminder = self.reminder
        if time is None:
            time = '-'
        if reminder is None:
            reminder = '-'

        return ('Name: "{}", key: {}, author: "{}", period: {}, '
                'activation time: {}, reminder: {}'.
                format(self.name, self.key, self.author, self.period, time,
                       reminder)
                )
