"""
This module contains functions for work with program's instances,
recognize user's console input and call library's functions for
work with program's entities
"""

# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логирование
# TODO: 4) еще можно выделить в сущность даже функции парсера!
import os
from app.formatted_argparse import FormattedParser
from app.help_functions import *
from app.parser_args import ParserArgs
from app.printer import Printer
from app.user_wrapper import (
    UserWrapper,
    UserWrapperStorage,
    UserWrapperController,
    LoginError,
    LogoutError,
    SaveUserError
)

try:
    from lib.calistra_lib.storage.json_serializer import JsonDatabase
    from lib.calistra_lib.user.user import User
    from lib.calistra_lib.task.task import Task, TaskStatus
    from lib.calistra_lib.task.queue import Queue
    from lib.calistra_lib.exceptions.base_exception import AppError
    from lib.calistra_lib.interface import Interface

except ImportError:
    from calistra_lib.storage.json_serializer import JsonDatabase
    from calistra_lib.user.user import User
    from calistra_lib.task.task import Task, TaskStatus
    from calistra_lib.task.queue import Queue
    from calistra_lib.exceptions.base_exception import AppError
    from calistra_lib.interface import Interface

FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
TASKS_FILE = os.path.join(FOLDER, 'tasks.json')
USERS_FILE = os.path.join(FOLDER, 'users.json')
AUTH_FILE = os.path.join(FOLDER, 'auth.json')
ONLINE = os.path.join(FOLDER, 'online_user.json')
FILES = [
    (TASKS_FILE, '[{"key": "0", "name": "__anon__",'
                 ' "owner": "guest", "opened": [], "solved": [], "failed": []}]'),
    (USERS_FILE, '[]'),
    (AUTH_FILE, '[]'),
    (ONLINE, '""')
]

ERROR_CODE = 1
BYTES_NUMBER = 8


def apply_settings():
    pass


def check_program_data_files(folder, files):
    if not os.path.exists(folder):
        os.mkdir(folder)
    for file in files:
        if not os.path.exists(file[0]):
            with open(file[0], 'w') as file_obj:
                file_obj.write(file[1])


def run() -> int:
    """
    Start program
    :return: int - exit code
    """
    # TODO: сделать функцию применения настроек
    # program settings
    apply_settings()
    check_program_data_files(FOLDER, FILES)

    parser = _get_parsers()
    args = vars(parser.parse_args())

    # check that target is defined
    target = args.pop(ParserArgs.TARGET.name)
    if target is None:
        parser.error('target is required')

    # check that action is defined
    action = args.pop(ParserArgs.ACTION)
    if action is None:
        FormattedParser.active_sub_parser.error('action is required')

    users_wrapper_storage = UserWrapperStorage(
        JsonDatabase(AUTH_FILE, [UserWrapper]),
        JsonDatabase(ONLINE, [])
    )

    library = Interface(
        users_wrapper_storage.online_user,
        JsonDatabase(USERS_FILE, [User]),
        JsonDatabase(TASKS_FILE, [Queue, Task])
    )

    # update reminders deadlines queue and other
    library.update_all()

    # check that target is user and do action with it
    if target == ParserArgs.USER.name:
        if action == ParserArgs.ADD:
            return _add_user(
                nick=args.pop(ParserArgs.NICKNAME.name),
                password=args.pop(ParserArgs.PASSWORD.name),
                users_storage=users_wrapper_storage,
                library=library
            )

        if action == ParserArgs.LOGIN.name:
            return _login(
                nick=args.pop(ParserArgs.NICKNAME.name),
                password=args.pop(ParserArgs.PASSWORD.name),
                users_storage=users_wrapper_storage,
                library=library
            )

        if action == ParserArgs.LOGOUT.name:
            return _logout(users_wrapper_storage)

        if action == ParserArgs.SHOW:
            return _show_user_tasks(library)

    # check that target is queue and do action with it
    if target == ParserArgs.QUEUE.name:
        if action == ParserArgs.ADD:
            return _add_queue(
                name=args.pop(ParserArgs.QUEUE_NAME.name).strip(' '),
                library=library
            )

        if action == ParserArgs.DELETE:
            return _del_queue(
                key=args.pop(ParserArgs.QUEUE_NAME.name).strip(' '),
                recursive=args.pop(ParserArgs.RECURSIVE.dest),
                library=library
            )

        if action == ParserArgs.SET:
            key = args.pop(ParserArgs.KEY.name)
            new_name = args.pop(ParserArgs.NEW_NAME.dest)
            if new_name is None:
                parser.active_sub_parser.help()
                return 0

            return _edit_queue(
                key=key,
                new_name=new_name,
                library=library
            )

        if action == ParserArgs.SHOW:
            return _show_queue_tasks(
                key=args.pop(ParserArgs.KEY.name),
                opened=args.pop(ParserArgs.OPEN_TASKS.dest),
                archive=args.pop(ParserArgs.SOLVED_TASKS.dest),
                failed=args.pop(ParserArgs.FAILED_TASKS.dest),
                long=args.pop(ParserArgs.LONG.dest),
                library=library
            )

    # check that target is task and do action with it
    if target == ParserArgs.TASK.name:
        if action == ParserArgs.ADD:
            return _add_task(args, library)

        if action == ParserArgs.SET:
            return _edit_task(args, library)

        if action == ParserArgs.DELETE:
            return _del_task(args, library)

        if action == ParserArgs.SHOW:
            return _show_task(
                args.pop(ParserArgs.KEY.name),
                library,
                args.pop(ParserArgs.LONG.dest)
            )

        if action == ParserArgs.FIND:
            return _find_task(args.pop(ParserArgs.TASK_NAME.name), library)

    # check that target is plan and do action with it
    if target == ParserArgs.PLAN.name:
        if action == ParserArgs.ADD:
            pass

    if target == ParserArgs.NOTIFICATIONS.name:
        if action == ParserArgs.SHOW:
            _show_notifications(library)

        if action == ParserArgs.DELETE:
            _del_notifications(
                library,
                _all=args.pop(ParserArgs.ALL.dest),
                old=args.pop(ParserArgs.OLD.dest)
            )


# =================================================
# functions for work with user's account instance =
# =================================================
def _add_user(nick, password, users_storage, library: Interface):
    try:
        users_storage.add_user(nick, password)
    except SaveUserError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        library.add_user(nick)
        print('User "{}" successfully created'.format(nick))
        return 0


def _login(nick, password, users_storage, library) -> int:
    controller = UserWrapperController(users_storage)
    try:
        controller.login(nick, password)
    except LoginError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('User "{}" now is online'.format(nick))
        library.set_online_user(nick)
        _show_notifications(library)
        return 0


def _logout(users_storage) -> int:
    controller = UserWrapperController(users_storage)
    try:
        controller.logout()
    except LogoutError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('All users now offline')
        return 0


def _show_notifications(library) -> int:
    notifications = library.online_user.notifications
    if notifications:
        print('Notifications for user "{}":'.
              format(library.online_user.nick)
              )

        reminders = []
        for notification in notifications:  # type: str
            if notification.lower().startswith('reminder'):
                reminders.append(notification)
                notifications.remove(notification)
        Printer.print_reminders(reversed(reminders))
        Printer.print_notifications(reversed(notifications))
    else:
        print('New notifications not found!')
    return 0


def _del_notifications(library, _all, old) -> int:
    try:
        library.clear_notifications(old)
    except ValueError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    return 0


def _show_user_tasks(library) -> int:
    try:
        print('User: "{}".'.format(library.online_user.nick))
        queues = library.get_user_queues()
        Printer.print_queues(queues)
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    author_tasks, responsible_tasks = library.get_user_tasks()
    print('Tasks:')
    Printer.print_tasks(author_tasks, "Author")
    Printer.print_tasks(responsible_tasks, "Responsible")
    return 0


# =================================================
# functions for work with queue instance          =
# =================================================
def _add_queue(name, library):
    key = os.urandom(BYTES_NUMBER).hex()
    try:
        added_queue = library.add_queue(name=name, key=key)
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('Queue "{}" added. It\'s key - {}'.format(
            added_queue.name, key))
        return 0


def _del_queue(key, recursive, library):
    try:
        deleted_queue = library.del_queue(
            key=key,
            recursive=recursive)
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('Queue "{}" deleted'.format(deleted_queue.name))
        return 0


def _edit_queue(key, new_name, library):
    try:
        new_name = check_str_len(new_name)
    except ValueError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        try:
            library.edit_queue(key, new_name)
        except AppError as e:
            print(e, file=sys.stderr)
            return ERROR_CODE
        else:
            print('Queue "{}" now have new name "{}"'.format(key, new_name))
            return 0


def _show_queue(library) -> int:
    # TODO: сделать чтобы показывались все таски
    try:
        queues = library.get_user_queues()
        if not queues:
            raise AppError('Queues not found')
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        for queue in queues:
            print('Queue name: "{}", key = {}'.format(
                queue.name, queue.key)
            )
        return 0


def _show_queue_tasks(key, library, opened, archive, failed, long):
    if not opened and not archive and not failed:
        opened = True
    try:
        queue = library.get_queue(key)
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('Queue: "{}", key {}\nTasks:'.format(queue.name, queue.key))
        if opened:
            Printer.print_tasks(queue.opened, TaskStatus.OPENED, long,
                                Printer.CL_YELLOW)
        if archive:
            Printer.print_tasks(queue.solved, TaskStatus.SOLVED, long,
                                Printer.CL_BLUE)
        if failed:
            Printer.print_tasks(queue.failed, TaskStatus.FAILED, long,
                                Printer.CL_RED)
        return 0


# =================================================
# functions for work with task instance           =
# =================================================
def _add_task(args, library) -> int:
    key = os.urandom(BYTES_NUMBER).hex()

    try:
        name = args.pop(ParserArgs.TASK_NAME.name).strip(' ')
        name = check_str_len(name)

        description = args.pop(ParserArgs.TASK_DESCRIPTION.dest)
        description = check_str_len(description)

        queue_name = args.pop(ParserArgs.TASK_QUEUE.dest).strip(' ')
        queue_name = check_str_len(queue_name)

        linked = args.pop(ParserArgs.TASK_LINKED.dest)
        linked = check_link_correctness(linked)

        responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
        responsible = check_responsible_correctness(responsible)

        priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
        priority = check_priority_correctness(priority)

        progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
        progress = check_progress_correctness(progress)

        start = args.pop(ParserArgs.TASK_START.dest)
        start = check_time_format(start)

        deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
        deadline = check_time_format(deadline)

        tags = args.pop(ParserArgs.TASK_TAGS.dest)
        tags = check_tags_correctness(tags)

        reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
        reminder = check_reminder_format(reminder)

    except ValueError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        try:
            library.add_task(
                name=name,
                queue_key=queue_name,
                description=description,
                parent=args.pop(ParserArgs.TASK_PARENT.dest),
                linked=linked,
                responsible=responsible,
                priority=priority,
                progress=progress,
                start=start,
                deadline=deadline,
                tags=tags,
                reminder=reminder,
                key=key
            )

        except AppError as e:
            print(e, file=sys.stderr)
            return ERROR_CODE
        else:
            print('Task "{}" added. It\'s key - {}'.format(name, key))
            return 0


def _edit_task(args, library) -> int:
    # TODO: продолжить делать этот метод
    key = args.pop(ParserArgs.KEY.name)

    try:
        name = args.pop(ParserArgs.NEW_NAME.dest)
        name = check_str_len(name)

        description = args.pop(ParserArgs.TASK_DESCRIPTION.dest)
        description = check_str_len(description)

        linked = args.pop(ParserArgs.TASK_LINKED.dest)
        linked = check_link_correctness(linked, action=ParserArgs.SET)

        responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
        responsible = check_responsible_correctness(responsible,
                                                    action=ParserArgs.SET)

        priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
        priority = check_priority_correctness(priority, action=ParserArgs.SET)

        progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
        progress = check_progress_correctness(progress, action=ParserArgs.SET)

        start = args.pop(ParserArgs.TASK_START.dest)
        start = check_time_format(start, action=ParserArgs.SET)

        deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
        deadline = check_time_format(deadline, action=ParserArgs.SET)

        tags = args.pop(ParserArgs.TASK_TAGS.dest)
        tags = check_tags_correctness(tags, action=ParserArgs.SET)

        reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
        reminder = check_reminder_format(reminder, action=ParserArgs.SET)

        status = args.pop(ParserArgs.TASK_STATUS.dest)
        status = check_status_correctness(status, action=ParserArgs.SET)
    except ValueError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        try:
            library.edit_task(
                key=key,
                name=name,
                description=description,
                status=status,
                parent=args.pop(ParserArgs.TASK_PARENT.dest),
                linked=linked,
                responsible=responsible,
                priority=priority,
                progress=progress,
                start=start,
                deadline=deadline,
                tags=tags,
                reminder=reminder,
            )
        except AppError as e:
            print(e, file=sys.stderr)
            return ERROR_CODE
        else:
            print('Task with key "{}" edited'.format(key))
            return 0


def _del_task(args, library) -> int:
    key = args.pop(ParserArgs.KEY.name)
    try:
        library.del_task(
            key=key,
            recursive=args.pop(ParserArgs.RECURSIVE.dest)
        )
    except AppError as e:
        print(e, file=sys.stderr)
        return ERROR_CODE
    else:
        print('Task with key "{}" deleted'.format(key))
    return 0


def _show_task(key, library, long) -> int:
    try:
        task = library.find_task(key=key)
    except AppError as e:
        print(e, file=sys.stderr)
    else:
        print('Main task:')
        Printer.print_task_briefly(task)
        sub_tasks = library.task_controller.find_sub_tasks(task)
        if sub_tasks:
            Printer.print_tasks(sub_tasks, "Sub tasks:")
    return 0


def _find_task(name, library) -> int:
    tasks = library.find_task(name=name)
    print('Search:')
    Printer.print_tasks(tasks, 'Result for "{}"'.format(name))
    return 0


# ===================================================
# private functions. Don't use outside this module! =
# ===================================================
def _get_parsers():
    """
    Init parser's attributes, create parsers and subparsers
    :return parser - main parser
    """
    parser = FormattedParser(
        description=ParserArgs.DESCRIPTION)
    subparsers = parser.add_subparsers(
        dest=ParserArgs.TARGET.name,
        help=ParserArgs.TARGET.help)

    # create next level parsers for different targets
    user_parser = subparsers.add_parser(
        name=ParserArgs.USER.name,
        help=ParserArgs.USER.help)

    queue_parser = subparsers.add_parser(
        name=ParserArgs.QUEUE.name,
        help=ParserArgs.QUEUE.help)

    task_parser = subparsers.add_parser(
        name=ParserArgs.TASK.name,
        help=ParserArgs.TASK.help)

    plan_parser = subparsers.add_parser(
        name=ParserArgs.PLAN.name,
        help=ParserArgs.PLAN.help)

    notifications_parser = subparsers.add_parser(
        name=ParserArgs.NOTIFICATIONS.name,
        help=ParserArgs.NOTIFICATIONS.help
    )

    # check console args, create subparsers for necessary args
    if ParserArgs.USER.name in sys.argv:
        FormattedParser.active_sub_parser = user_parser
        _create_user_subparsers(user_parser)

    elif ParserArgs.QUEUE.name in sys.argv:
        FormattedParser.active_sub_parser = queue_parser
        _create_queue_subparsers(queue_parser)

    elif ParserArgs.TASK.name in sys.argv:
        FormattedParser.active_sub_parser = task_parser
        _create_task_subparsers(task_parser)

    elif ParserArgs.PLAN.name in sys.argv:
        FormattedParser.active_sub_parser = plan_parser
        _create_plan_subparsers(plan_parser)

    elif ParserArgs.NOTIFICATIONS.name in sys.argv:
        FormattedParser.active_sub_parser = notifications_parser
        _create_notification_subparsers(notifications_parser)

    return parser


def _create_user_subparsers(user_parser):
    """
    Create subparsers for processing user's data
    :return: None
    """
    user_subparsers = user_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.USER_ACTION)

    # calistra user add <nickname> <password>
    add_subparsers = user_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_USER_HELP)

    # calistra user login <nickname> <password>
    login_subparsers = user_subparsers.add_parser(
        name=ParserArgs.LOGIN.name,
        help=ParserArgs.LOGIN.help)

    # calistra user logout (only for online user)
    logout_subparsers = user_subparsers.add_parser(
        name=ParserArgs.LOGOUT.name,
        help=ParserArgs.LOGOUT.help)

    # calistra user show
    show_subparsers = user_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_USER_HELP)

    if ParserArgs.ADD in sys.argv:
        # calistra user add <nickname>
        add_subparsers.add_argument(
            dest=ParserArgs.NICKNAME.name,
            help=ParserArgs.NICKNAME.help)

        # calistra user add <password>
        add_subparsers.add_argument(
            dest=ParserArgs.PASSWORD.name,
            help=ParserArgs.PASSWORD.help)
        # set add_subparsers as active
        FormattedParser.active_sub_parser = add_subparsers

    elif ParserArgs.LOGIN.name in sys.argv:
        login_subparsers.add_argument(
            dest=ParserArgs.NICKNAME.name,
            help=ParserArgs.NICKNAME.help)
        login_subparsers.add_argument(
            dest=ParserArgs.PASSWORD.name,
            help=ParserArgs.PASSWORD.help)
        # set login_subparsers as active
        FormattedParser.active_sub_parser = login_subparsers

    elif ParserArgs.SHOW in sys.argv:
        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.LOGOUT.name in sys.argv:
        FormattedParser.active_sub_parser = logout_subparsers


# TODO: добавить документацию и опциональные параметры
def _create_queue_subparsers(queue_parser):
    queue_subparsers = queue_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.QUEUE_ACTION)

    # calistra queue add
    add_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_QUEUE_HELP)

    # calistra queue set
    edit_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_QUEUE_HELP)

    # calistra queue del
    del_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DELETE_QUEUE_HELP)

    # calistra queue show
    show_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_QUEUE_HELP)

    if ParserArgs.ADD in sys.argv:
        # calistra queue add <name>
        add_subparsers.add_argument(
            dest=ParserArgs.QUEUE_NAME.name,
            help=ParserArgs.QUEUE_NAME.help)
        # set add_subparsers as active
        FormattedParser.active_sub_parser = add_subparsers

    elif ParserArgs.SET in sys.argv:
        # calistra queue set <name>
        edit_subparsers.add_argument(
            dest=ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        # calistra queue set <name> <new_name>
        edit_subparsers.add_argument(
            ParserArgs.NEW_NAME.long,
            dest=ParserArgs.NEW_NAME.dest,
            help=ParserArgs.NEW_NAME.help)

        FormattedParser.active_sub_parser = edit_subparsers

    elif ParserArgs.DELETE in sys.argv:
        # calistra queue del <name>
        del_subparsers.add_argument(
            dest=ParserArgs.QUEUE_NAME.name,
            help=ParserArgs.QUEUE_NAME.help)

        del_subparsers.add_argument(
            ParserArgs.RECURSIVE.short,
            ParserArgs.RECURSIVE.long,
            dest=ParserArgs.RECURSIVE.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.RECURSIVE.help
        )

        FormattedParser.active_sub_parser = del_subparsers

    elif ParserArgs.SHOW in sys.argv:
        # calistra queue show <key>
        show_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help
        )

        show_subparsers.add_argument(
            ParserArgs.LONG.long,
            ParserArgs.LONG.short,
            dest=ParserArgs.LONG.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.LONG.help
        )

        show_subparsers.add_argument(
            ParserArgs.OPEN_TASKS.long,
            dest=ParserArgs.OPEN_TASKS.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.OPEN_TASKS.help
        )

        show_subparsers.add_argument(
            ParserArgs.SOLVED_TASKS.long,
            dest=ParserArgs.SOLVED_TASKS.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.SOLVED_TASKS.help
        )

        show_subparsers.add_argument(
            ParserArgs.FAILED_TASKS.long,
            dest=ParserArgs.FAILED_TASKS.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.FAILED_TASKS.help
        )

        FormattedParser.active_sub_parser = show_subparsers


def _create_task_subparsers(task_parser):
    """Create subparsers for processing task's data
    :param task_parser
    :return None
    """
    task_subparsers = task_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.TASK_ACTION)

    # calistra task add
    add_subparsers = task_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_TASK_HELP)

    # calistra task set
    edit_subparsers = task_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_TASK_HELP)

    # calistra task delete
    del_subparsers = task_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DELETE_TASK_HELP)

    # calistra task show
    show_subparsers = task_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_TASK_HELP)

    find_subparsers = task_subparsers.add_parser(
        name=ParserArgs.FIND,
        help=ParserArgs.FIND_TASK_HELP
    )

    if ParserArgs.ADD in sys.argv:
        # positional args for add_subparsers
        # calistra task add <name>
        add_subparsers.add_argument(
            dest=ParserArgs.TASK_NAME.name,
            help=ParserArgs.TASK_NAME.help)

        # add optional arguments
        __add_common_optional_task_args(add_subparsers)

        # calistra task add [--queue=<QUEUE>]
        add_subparsers.add_argument(
            ParserArgs.TASK_QUEUE.long,
            dest=ParserArgs.TASK_QUEUE.dest,
            default='?',
            help=ParserArgs.TASK_QUEUE.help)

        FormattedParser.active_sub_parser = add_subparsers

    elif ParserArgs.SET in sys.argv:
        # positional args for edit_subparsers
        # calistra task set <TASK_KEY>
        edit_subparsers.add_argument(
            dest=ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        # optional args for edit_subparsers
        # calistra task set --new_name=<NEW_NAME>
        edit_subparsers.add_argument(
            ParserArgs.NEW_NAME.long,
            dest=ParserArgs.NEW_NAME.dest,
            help=ParserArgs.NEW_NAME.help)

        # calistra task set --status=<STATUS>
        edit_subparsers.add_argument(
            ParserArgs.TASK_STATUS.long,
            dest=ParserArgs.TASK_STATUS.dest,
            help=ParserArgs.TASK_STATUS.help)

        __add_common_optional_task_args(edit_subparsers)

        FormattedParser.active_sub_parser = edit_subparsers

    elif ParserArgs.DELETE in sys.argv:
        # positional args for del_subparsers
        # calistra task del <TASK_KEY>
        del_subparsers.add_argument(
            dest=ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        # optional args for del_subparsers
        # calistra task del [-r]
        del_subparsers.add_argument(
            ParserArgs.RECURSIVE.short,
            ParserArgs.RECURSIVE.long,
            dest=ParserArgs.RECURSIVE.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.RECURSIVE.help)

        FormattedParser.active_sub_parser = del_subparsers

    elif ParserArgs.SHOW in sys.argv:
        show_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        show_subparsers.add_argument(
            ParserArgs.LONG.short,
            ParserArgs.LONG.long,
            action=ParserArgs.__STORE_TRUE__,
            dest=ParserArgs.LONG.dest,
            help=ParserArgs.LONG.help
        )
        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.FIND in sys.argv:
        find_subparsers.add_argument(
            ParserArgs.TASK_NAME.name,
            help=ParserArgs.TASK_NAME.help)

        FormattedParser.active_sub_parser = find_subparsers


def __add_common_optional_task_args(action_subparser):
    # calistra task <action> [--description=<DESCR>]
    action_subparser.add_argument(
        ParserArgs.TASK_DESCRIPTION.long,
        dest=ParserArgs.TASK_DESCRIPTION.dest,
        help=ParserArgs.TASK_DESCRIPTION.help)

    # calistra task <action> [--parent=<PARENT>]
    action_subparser.add_argument(
        ParserArgs.TASK_PARENT.long,
        dest=ParserArgs.TASK_PARENT.dest,
        help=ParserArgs.TASK_PARENT.help)

    # calistra task <action> [--linked=<LINKED>]
    action_subparser.add_argument(
        ParserArgs.TASK_LINKED.long,
        dest=ParserArgs.TASK_LINKED.dest,
        help=ParserArgs.TASK_LINKED.help)

    # calistra task <action> [--responsible=<RESP>]
    action_subparser.add_argument(
        ParserArgs.TASK_RESPONSIBLE.long,
        dest=ParserArgs.TASK_RESPONSIBLE.dest,
        help=ParserArgs.TASK_RESPONSIBLE.help)

    # calistra task <action> [--priority=<PRIOR>]
    action_subparser.add_argument(
        ParserArgs.TASK_PRIORITY.long,
        dest=ParserArgs.TASK_PRIORITY.dest,
        help=ParserArgs.TASK_PRIORITY.help)

    # calistra task <action> [--progress=<PROGRESS>]
    action_subparser.add_argument(
        ParserArgs.TASK_PROGRESS.long,
        dest=ParserArgs.TASK_PROGRESS.dest,
        help=ParserArgs.TASK_PROGRESS.help)

    # calistra task <action> [--starts=<START>]
    action_subparser.add_argument(
        ParserArgs.TASK_START.long,
        dest=ParserArgs.TASK_START.dest,
        help=ParserArgs.TASK_START.help)

    # calistra task <action> [--deadline=<DEADLINE>]
    action_subparser.add_argument(
        ParserArgs.TASK_DEADLINE.long,
        dest=ParserArgs.TASK_DEADLINE.dest,
        help=ParserArgs.TASK_DEADLINE.help)

    # calistra task <action> [--tags=<TAGS>]
    action_subparser.add_argument(
        ParserArgs.TASK_TAGS.long,
        dest=ParserArgs.TASK_TAGS.dest,
        help=ParserArgs.TASK_TAGS.help)

    # calistra task <action> [--reminder=<REMINDER>]
    action_subparser.add_argument(
        ParserArgs.TASK_REMINDER.long,
        dest=ParserArgs.TASK_REMINDER.dest,
        help=ParserArgs.TASK_REMINDER.help)


def _create_plan_subparsers(plan_parser):
    """Create subparsers for processing plan's data
    :param plan_parser
    :return None
    """
    plan_subparsers = plan_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.PLAN_ACTION)


def _create_notification_subparsers(notification_parser):
    notification_subparsers = notification_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.NTF_ACTION
    )

    show_subparsers = notification_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_NTF_HELP
    )

    del_subparsers = notification_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DELETE_NTF
    )

    if ParserArgs.SHOW in sys.argv:
        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.DELETE in sys.argv:
        group = del_subparsers.add_mutually_exclusive_group()
        group.add_argument(
            ParserArgs.ALL.long,
            dest=ParserArgs.ALL.dest,
            action=ParserArgs.__STORE_TRUE__,
            help=ParserArgs.ALL.help
        )

        group.add_argument(
            ParserArgs.OLD.long,
            type=int,
            dest=ParserArgs.OLD.dest,
            help=ParserArgs.OLD.help
        )
        FormattedParser.active_sub_parser = del_subparsers
