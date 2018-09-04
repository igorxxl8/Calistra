from django.core.exceptions import ValidationError
from calistra_lib.task.reminder import Reminder


def validate_reminder(value):
    reminder = Reminder.check_format(value)
    if reminder is False:
        raise ValidationError('Invalid reminder format: "{}"'.format(value),
                              params={'value': value})


def validate_time_format(value):
    pass
