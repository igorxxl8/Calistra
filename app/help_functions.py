from datetime import datetime
try:
    from lib.calistra_lib.task.task import TaskStatus
except ImportError:
    from calistra_lib.task.task import TaskStatus

TIME_FORMAT = '%d.%m.%Y.%H:%M'


# TODO: сделать корректные сообщения об ошибках для консоли и для веба отдельно
# TODO: сделав тем самым константу какую нибудь

def concat(*args):
    return ''.join(args)


def check_str_len(string):
    if isinstance(string, str) and len(string) > 100:
        raise ValueError('calistra: description and name must not '
                         'exceed 100 characters')
    return string


def check_priority_correctness(priority, action='add'):
    #  to check if the priority is entered correctly
    priority_dict = {'high': "10", 'low': "-10", 'medium': "0"}
    if priority is None:
        return None
    if priority in priority_dict.keys():
        priority = priority_dict[priority]
    try:
        priority = int(priority)
        if 10 < priority or priority < -10:
            raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: incorrect value of priority. '
                                'See "calistra task ', action, ' --help"'))
    return priority


def check_status_correctness(status, action='add'):
    if status is None:
        return None
    if status not in TaskStatus.__dict__.values():
        raise ValueError(concat('calistra: incorrect value of status. '
                                'See "calistra task ', action, ' --help"'))

    return status


def check_progress_correctness(progress, action='add'):
    try:
        if progress is None or progress == '?':
            return None
        progress = int(progress)
        if 100 < progress or progress < 0:
            raise ValueError()
    except ValueError:
        raise ValueError(concat('calistra: incorrect value of progress. '
                                'See "calistra task ', action, ' --help"'))
    return progress


def check_time_format(time, action='add'):
    if time == '?':
        return '?'
    try:
        if time is None:
            return None
        datetime.strptime(time, TIME_FORMAT)
    except ValueError:
        raise ValueError(
            concat('calistra: invalid format of date and time. See '
                   '"calistra task ', action, ' --help"')
        )

    return time


def check_tags_correctness(tags_to_check: str, action='add'):
    try:
        return check_list_format_correctness(tags_to_check, 'tags', action)
    except ValueError as e:
        raise ValueError(e)


def check_list_format_correctness(objects_list: str, obj_type, action, ):
    if objects_list == '?':
        return '?'
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
                                '. See "calistra task ', action, ' --help"'))

    return right_list


def check_reminder_format(reminder, action='add'):
    return reminder


def check_link_correctness(linked, action='add'):
    return linked


def check_responsible_correctness(responsible, action='add'):
    try:
        return check_list_format_correctness(responsible, 'responsible', action)
    except ValueError as e:
        raise ValueError(e)
