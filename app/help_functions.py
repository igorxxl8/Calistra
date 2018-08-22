from datetime import datetime as dt

try:
    from lib.calistra_lib.task.reminder import Reminder
    from lib.calistra_lib.constants import Constants
    from lib.calistra_lib.task.task import TaskStatus, RelatedTaskType
except ImportError:
    from calistra_lib.task.reminder import Reminder
    from calistra_lib.constants import Constants
    from calistra_lib.task.task import TaskStatus, RelatedTaskType

# TODO: сделать корректные сообщения об ошибках для консоли и для веба отдельно
# TODO: сделав тем самым константу какую нибудь

ADD = 'add'


def concat(*args):
    return ''.join(args)


def get_date(string):
    return dt.strptime(string, Constants.TIME_FORMAT)


def check_str_len(string):
    if isinstance(string, str) and len(string) > 100:
        raise ValueError('calistra: description and name must not '
                         'exceed 100 characters')
    return string


def check_priority_correctness(priority, action=ADD):
    #  to check if the priority is entered correctly
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
    if status is None:
        return None
    if status not in TaskStatus.__dict__.values():
        raise ValueError(concat('calistra: incorrect value of status. '
                                'See "calistra task ', action, ' --help\n"'))

    return status


def check_progress_correctness(progress, action=ADD):
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


def check_time_format(time, action=ADD):
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
                   '"calistra task ', action, ' --help\n"')
        )

    return time


def check_terms_correctness(start, deadline):
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
    if tags == Constants.UNDEFINED and action == ADD:
        return None

    try:
        return check_list_format_correctness(tags, 'tags', action)
    except ValueError as e:
        raise ValueError(e)


def check_list_format_correctness(objects_list: str, obj_type, action, ):
    if objects_list == Constants.UNDEFINED:
        return Constants.UNDEFINED
    if objects_list is None:
        return None
    objects_list = objects_list.split(',')
    right_list = []
    try:
        for obj in objects_list:
            checked_obj = obj.strip(' ')
            right_list.append(checked_obj)
            if not checked_obj:
                raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: invalid format of ', obj_type,
                                '. See "calistra task ', action, ' --help\n"'))

    return right_list


def check_reminder_format(reminder, action=ADD):
    reminder = Reminder.check_format(reminder)
    if reminder is False:
        raise ValueError(concat('calistra: invalid format of reminder. '
                                'See "calistra task ', action, ' --help\n'))

    return reminder


def check_related_correctness(related, action=ADD):
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
    if responsible == Constants.UNDEFINED and action == ADD:
        return []

    try:
        return check_list_format_correctness(responsible, 'responsible', action)
    except ValueError as e:
        raise ValueError(e)
