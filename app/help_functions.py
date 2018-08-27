"""This module contains functions for check user console input on correctness"""

from datetime import datetime as dt
from calistra_lib.task.reminder import Reminder
from calistra_lib.constants import Constants, Time, PlanPeriod
from calistra_lib.task.task import TaskStatus, RelatedTaskType

ADD = 'add'


def concat(*args):
    """
    This function join all substring in one string
    :param args: list of substrings
    :return: joint string
    """
    return ''.join(args)


def get_date(string):
    """
    This function transform date from string in datetime object in special
    program format
    :param string: string in time format
    :return: datetime object
    """
    return dt.strptime(string, Time.DATETIME_FORMAT)


def check_str_len(string):
    """
    This function check string length and if it isn't correct raise error
    :raise: ValueError
    :param string: string for checking
    :return: string
    """
    if isinstance(string, str) and 100 < len(string) < 1:
        raise ValueError('calistra: description and name must not '
                         'exceed 100 characters or be empty.\n')
    return string


def check_priority_correctness(priority, action=ADD):
    """
    This function check priority format correctness and converts string
    constants (high, low, medium) in numbers
    :param priority: value of priority
    :param action: action with entity (add, set)
    :raise ValueError
    :return: priority as digit
    """
    priority_dict = {'high': "10", 'low': "-10", 'medium': "0"}
    if priority is None:
        if action == ADD:
            return 0
        return None
    if priority in priority_dict.keys():
        priority = priority_dict[priority]
    try:
        priority = int(priority)
        if 10 < priority or priority < -10:
            raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: incorrect value of priority. '
                                'See "calistra task ', action, ' --help\n"'))
    return priority


def check_status_correctness(status, action=ADD):
    """
    This function check match of TaskStatus choices with user input status
    :param status: value of status
    :param action: action with entity (add, set)
    :raise ValueError
    :return: status
    """
    if status is None:
        return None
    if status not in TaskStatus.__dict__.values():
        raise ValueError(concat('calistra: incorrect value of status. '
                                'See "calistra task ', action, ' --help\n"'))

    return status


def check_progress_correctness(progress, action=ADD):
    """
    This function check match of progress format
    :param progress: progress as string
    :param action: action with entity (add, set)
    :raise ValueError
    :return: progress ass number
    """
    try:
        if progress == Constants.UNDEFINED:
            return None

        if progress is None:
            if action == ADD:
                return 0
            return None

        progress = int(progress)
        if 100 < progress or progress < 0:
            raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: incorrect value of progress. '
                                'See "calistra task ', action, ' --help\n"'))
    return progress


def check_time_format(time, entity, action=ADD):
    """
    This method check time format correctness
    :raise ValueError
    :param time in string format
    :param entity: plan or task
    :param action: add or set
    :return: time
    """
    if time is None:
        return None

    if time == Constants.UNDEFINED:
        if action == ADD:
            return None
        return Constants.UNDEFINED

    try:
        get_date(time)
    except ValueError:
        raise ValueError(
            concat('calistra: invalid format of date and time. See '
                   '"calistra ', entity, ' ', action, ' --help\n"')
        )

    return time


def validate_activation_time(time):
    """
    This function check that activation time not earlier than current moment
    :param time: activation time
    :raise ValueError
    :return: None
    """
    if get_date(time) < dt.now():
        raise ValueError('calistra: activation time cannot be earlier '
                         'than current moment.\n')


def check_period_format(period, action=ADD):
    """
    This function check that period has right format
    :param period:
    :param action: action with entity (add or set)
    :raise ValueError
    :return: None
    """
    if period not in PlanPeriod.__dict__.values():
        raise ValueError(concat('calistra: invalid format of plan period. See '
                                '"calistra plan ', action, ' --help"\n'))


def check_terms_correctness(start, deadline):
    """
    This method check deadline and start on correctness of time format
    and that deadline is not earlier than start and they both are not
     earlier than current moment
    :param start: time of start task
    :param deadline: time of end task
    :raise ValueError
    :return: None
    """
    if deadline:
        deadline_date = get_date(deadline)
        if deadline_date < dt.now():
            raise ValueError(
                'calistra: Deadline error: deadline cannot be earlier than '
                'current time.\n')

        if start and (deadline_date < get_date(start)):
            raise ValueError('calistra: Deadline error: the deadline for a task'
                             ' cannot be earlier than its start.\n')


def check_tags_correctness(tags: str, action=ADD):
    """
    This function check matching of tags and its format
    :param tags:
    :param action: action witch entity(add or set)
    :raise ValueError
    :return: None
    """
    if tags == Constants.UNDEFINED and action == ADD:
        return None

    try:
        return check_list_format_correctness(tags, 'tags', action)
    except ValueError as e:
        raise ValueError(e)


def check_list_format_correctness(objects_list: str, obj_type, action):
    """
    This function check that list of objects in string format matching
    necessary format of list and transform it into list
    :param objects_list: list of objects as string for checking
    :param obj_type: type of this objects
    :param action: action with entity(add or set)
    :raise ValueError
    :return: right_list: list of objects in list format
    """
    if objects_list == Constants.UNDEFINED:
        return Constants.UNDEFINED
    if objects_list is None:
        return None

    # split string by comma and form list of strings
    objects_list = objects_list.split(',')
    right_list = []
    try:
        # append every string if it correct to right list
        for obj in objects_list:
            checked_obj = obj.strip(' ')
            right_list.append(checked_obj)
            # if string is space or nothing raise error
            if not checked_obj:
                raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: invalid format of ', obj_type,
                                '. See "calistra task ', action, ' --help\n"'))

    return right_list


def check_reminder_format(reminder, entity, action=ADD):
    """
    This function check that reminder match special format frequency:time
    :param reminder: reminder in string format
    :param entity: plan or task
    :param action: action with entity (add or set)
    :raise ValueError
    :return: reminder
    """
    if reminder == Constants.UNDEFINED and action != ADD:
        return
    reminder = Reminder.check_format(reminder)
    if reminder is False:
        raise ValueError(concat('calistra: invalid format of reminder. '
                                'See "calistra ', entity, ' ', action,
                                ' --help"\n')
                         )

    return reminder


def check_related_correctness(related, action=ADD):
    """
    This function check that string for define related task has correct format
    :param related: string
    :param action: action with entity (add or set)
    :raise ValueError
    :return: None
    """
    if related == Constants.UNDEFINED and action != ADD:
        return Constants.UNDEFINED
    if related is None:
        return None
    try:
        attrs = related.split(':')

        if len(attrs) != 2 or attrs[1] not in RelatedTaskType.__dict__.values():
            raise ValueError()

    except ValueError as e:
        raise ValueError(concat('calistra: invalid format of related tasks. '
                                'See "calistra task ', action, ' --help\n"'))


def check_responsible_correctness(responsible, action=ADD):
    """
    This function check that string for define task responsible user keys
    is in correct format
    :param responsible: string
    :param action: action with entity (add or set)
    :raise ValueError
    :return: empty list
    """
    if responsible == Constants.UNDEFINED and action == ADD:
        return []

    try:
        return check_list_format_correctness(responsible, 'responsible', action)
    except ValueError as e:
        raise ValueError(e)
