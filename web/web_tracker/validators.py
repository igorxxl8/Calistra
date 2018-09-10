from django.core.exceptions import ValidationError
from calistra_lib.task.reminder import Reminder
from datetime import datetime as dt
from calistra_web.settings import TIME_FORMAT, TIME_FORMAT_WITH_SECONDS
from calistra_lib.task.task import RelatedTaskType


def get_date(string):
    return dt.strptime(string, TIME_FORMAT)


def validate_reminder(value):
    reminder = Reminder.check_format(value)
    if reminder is False:
        raise ValidationError('Invalid reminder format: "{}"!'.format(value),
                              params={'value': value})


def validate_queue_name(value):
    if value.upper() == 'DEFAULT':
        raise ValidationError('Name "{}" is reserved!'.format(value),
                              params={'value': value})


def validate_time_format(value):
    if value == "['', '']":
        value = None
        return value
    try:
        get_date(value)
    except Exception:
        raise ValidationError('Invalid date/time format!'.format(value),
                              params={'value': value})


def validate_deadline(value):
    try:
        if validate_time_format(value) is None:
            value = None
            return value
    except ValidationError as e:
        raise e
    if get_date(value) < dt.now():
        raise ValidationError(
            'Deadline cannot be earlier than now!'.format(value),
            params={'value': value})


def validate_related(value):
    attrs = value.split(':')

    if len(attrs) != 2 or attrs[1] not in RelatedTaskType.__dict__.values():
        raise ValidationError(
            'Invalid related format! Please use next format:'
            ' task_keys:related_type. '
            'Examples: regu453hj:controller, fsdferguer,'
            'regergfdgdsf:blocker'.format(value),
            params={'value': value})
