import sys

CHECKING_ERROR = 404


def check_priority_correctness(priority):
    #  to check if the priority is entered correctly
    priority_dict = {'high': "10", 'low': "-10", 'medium': "0"}
    if priority is None:
        priority = 0
    if priority in priority_dict.keys():
        priority = priority_dict[priority]
    try:
        priority = int(priority)
        if 10 < priority or priority < -10:
            raise ValueError()
    except ValueError:
        print('Incorrect value of priority. See --help/-h', file=sys.stderr)
        return CHECKING_ERROR
    else:
        return priority


def check_status_correctness(status):
    if status is None:
        return None
    if status not in ['opened', 'closed', 'solved', 'worked']:
        print('Incorrect value of status. See --help/-h', file=sys.stderr)
        return CHECKING_ERROR
    return status


def check_progress_correctness(progress):
    try:
        if progress is None:
            return 0
        progress = int(progress)
        if 100 < progress < 0:
            raise ValueError()
    except ValueError:
        print('Incorrect value of progress. See --help/-h', file=sys.stderr)
        return CHECKING_ERROR
    return progress


def check_time_format(time):
    return time


def check_tags_correctness(tags_to_check: str):
    if tags_to_check == '?':
        return '?'
    tags_to_check = tags_to_check.split(',')
    right_tags = []
    try:
        for tag in tags_to_check:
            checked_tag = tag.strip(' ')
            right_tags.append(checked_tag)
            if not checked_tag:
                raise ValueError()
    except ValueError:
        print('Invalid format of tags. See --help/-h')
        return CHECKING_ERROR
    return right_tags


def check_reminder_format(reminder):
    return reminder


def check_link_correctness(linked):
    return linked


def check_responsible_correctness(responsible):
    return responsible
