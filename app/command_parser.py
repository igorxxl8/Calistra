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
from app.formatted_parser import FormattedParser
from app.help_functions import *
from app.parser_args import ParserArgs
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
    from lib.calistra_lib.task.task import Task
    from lib.calistra_lib.task.queue import Queue
    from lib.calistra_lib.library_interface.interface import (
        Interface,
        QueueError,
        TaskError
    )
except ImportError:
    from calistra_lib.storage.json_serializer import JsonDatabase
    from calistra_lib.user.user import User
    from calistra_lib.task.task import Task
    from calistra_lib.task.queue import Queue
    from calistra_lib.library_interface.interface import (
        Interface,
        QueueError,
        TaskError
    )

FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
TASKS_FILE = os.path.join(FOLDER, 'tasks.json')
USERS_FILE = os.path.join(FOLDER, 'users.json')
AUTH_FILE = os.path.join(FOLDER, 'auth.json')
ONLINE = os.path.join(FOLDER, 'online_user.json')
FILES = [
    (TASKS_FILE, '[{"name": "_inbox", "tasks": [], "archive": []}]'),
    (USERS_FILE, '[]'),
    (AUTH_FILE, '[]'),
    (ONLINE, '""')
]


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
    apply_settings()
    check_program_data_files(FOLDER, FILES)

    # sub_parser define message which print in case lack of necessary arguments
    parser, sub_parser = _get_parsers()
    args = vars(parser.parse_args())

    # check that target is defined
    target = args.pop(ParserArgs.TARGET.name)
    if target is None:
        parser.error('target is required')

    # check that action is defined
    action = args.pop(ParserArgs.ACTION)
    if action is None:
        sub_parser.error('action is required')

    users_wrapper_storage = UserWrapperStorage(
        JsonDatabase(AUTH_FILE, [UserWrapper]),
        JsonDatabase(ONLINE, [])
    )

    library_interface = Interface(
        users_wrapper_storage.online_user,
        JsonDatabase(USERS_FILE, [User]),
        JsonDatabase(TASKS_FILE, [Queue, Task])
    )

    # check that target is user and do action with it
    if target == ParserArgs.USER.name:
        if action == ParserArgs.ADD:
            return _add_user(
                nick=args.pop(ParserArgs.NICKNAME.name),
                password=args.pop(ParserArgs.PASSWORD.name),
                users_storage=users_wrapper_storage,
                library_interface=library_interface
            )

        if action == ParserArgs.LOGIN.name:
            return _login(
                nick=args.pop(ParserArgs.NICKNAME.name),
                password=args.pop(ParserArgs.PASSWORD.name),
                users_storage=users_wrapper_storage
            )

        if action == ParserArgs.LOGOUT.name:
            return _logout(users_wrapper_storage)

        if action == ParserArgs.SHOW:
            return _show_users(users_wrapper_storage)

    # check that target is queue and do action with it
    if target == ParserArgs.QUEUE.name:
        if action == ParserArgs.ADD:
            return _add_queue(
                name=args.pop(ParserArgs.QUEUE_NAME.name),
                library_interface=library_interface
            )

        if action == ParserArgs.DELETE:
            return _del_queue(
                name=args.pop(ParserArgs.QUEUE_NAME.name),
                recursive=args.pop(ParserArgs.RECURSIVE.dest),
                library_interface=library_interface
            )

        if action == ParserArgs.SET:
            return _set_queue_new_name(
                name=args.pop(ParserArgs.QUEUE_NAME.name),
                new_name=args.pop(ParserArgs.QUEUE_NEW_NAME.name),
                library_interface=library_interface
            )

        if action == ParserArgs.SHOW:
            name = args.pop(ParserArgs.TASK_QUEUE.dest)
            _all = args.pop(ParserArgs.ALL.dest)
            if name:
                return _show_queue_tasks(name, library_interface)
            if _all:
                return _show_queue(library_interface)

    # check that target is task and do action with it
    if target == ParserArgs.TASK.name:
        if action == ParserArgs.ADD:
            return _add_task(args, library_interface)

        if action == ParserArgs.SET:
            return _edit_task(args, library_interface)

        if action == ParserArgs.DELETE:
            return _del_task(args, library_interface)

    # check that target is plan and do action with it
    if target == ParserArgs.PLAN.name:
        if action == ParserArgs.ADD:
            pass


# =================================================
# functions for work with user's account instance =
# =================================================
def _add_user(nick, password, users_storage, library_interface: Interface):
    try:
        users_storage.add_user(nick, password)
    except SaveUserError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        library_interface.add_user(nick)
        print('User "{}" successfully created'.format(nick))
        return 0


def _login(nick, password, users_storage) -> int:
    controller = UserWrapperController(users_storage)
    try:
        controller.login(nick, password)
    except LoginError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('User "{}" now is online'.format(nick))
        return 0


def _logout(users_storage) -> int:
    controller = UserWrapperController(users_storage)
    try:
        controller.logout()
    except LogoutError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('All users now offline')
        return 0


def _show_users(storage) -> int:
    # TODO: сделать форматированный показ пользователей
    for user in storage.users:
        print('{}'.format(user.nick))
    return 0


# =================================================
# functions for work with queue instance          =
# =================================================
def _add_queue(name, library_interface):
    try:
        library_interface.add_queue(name=name)
    except QueueError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('Queue "{}" added'.format(name))
        return 0


def _del_queue(name, recursive, library_interface):
    try:
        # TODO: добавить опциональный аргумент рекурсии
        library_interface.del_queue(name=name, recursive=recursive)
    except QueueError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print("Queue '{}' deleted".format(name))
        return 0


def _set_queue_new_name(name, new_name, library_interface):
    try:
        library_interface.edit_queue(name, new_name)
    except QueueError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('Queue "{}" now have new name "{}"'.format(name, new_name))
    return 0


def _show_queue(library_interface) -> int:
    # TODO: сделать чтобы показывались все таски
    try:
        queues = library_interface.get_user_queues()
        if not queues:
            raise QueueError('Queues didn\'t found')
    except QueueError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        for queue in queues:
            print('Queue name: "{}"'.format(queue.name.split('_')[1]))
        return 0


def _show_queue_tasks(name, library_interface):
    # TODO: сделать форматированный показ тасок
    try:
        tasks = library_interface.get_queue_tasks(name)
    except QueueError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        for task in tasks:  # type: Task
            print('Name: "{}", key: {}'.format(task.name, task.key))
        return 0


# =================================================
# functions for work with task instance           =
# =================================================
def _add_task(args, lib_interface) -> int:
    name = args.pop(ParserArgs.TASK_NAME.name)
    queue_name = args.pop(ParserArgs.TASK_QUEUE.dest)
    key = os.urandom(8).hex()

    linked = args.pop(ParserArgs.TASK_LINKED.dest)
    linked = check_link_correctness(linked)
    if linked == CHECKING_ERROR:
        return 1

    responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
    responsible = check_responsible_correctness(responsible)
    if responsible == CHECKING_ERROR:
        return 1

    priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
    priority = check_priority_correctness(priority)
    if priority == CHECKING_ERROR:
        return 1

    progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
    progress = check_progress_correctness(progress)
    if progress == CHECKING_ERROR:
        return 1

    start = args.pop(ParserArgs.TASK_START.dest)
    start = check_time_format(start)
    if start == CHECKING_ERROR:
        return 1

    deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
    deadline = check_time_format(deadline)
    if deadline == CHECKING_ERROR:
        return 1

    tags = args.pop(ParserArgs.TASK_TAGS.dest)
    tags = check_tags_correctness(tags)
    if tags == CHECKING_ERROR:
        return 1

    reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
    reminder = check_reminder_format(reminder)
    if reminder == CHECKING_ERROR:
        return 1

    try:
        lib_interface.add_task(
            name=name,
            queue_name=queue_name,
            description=args.pop(ParserArgs.TASK_DESCRIPTION.dest),
            parent=args.pop(ParserArgs.TASK_PARENT.dest),
            linked=linked,
            responsible=responsible,
            priority=int(priority),
            progress=progress,
            start=start,
            deadline=deadline,
            tags=tags,
            reminder=reminder,
            key=key
        )

    except TaskError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('Task "{}" added in queue "{}"'.format(name, queue_name))
        return 0


def _edit_task(args, lib_interface) -> int:
    # TODO: продолжить делать этот метод
    key = args.pop(ParserArgs.TASK_KEY.name)

    linked = args.pop(ParserArgs.TASK_LINKED.dest)
    linked = check_link_correctness(linked)
    if linked == CHECKING_ERROR:
        return 1

    responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
    responsible = check_responsible_correctness(responsible)
    if responsible == CHECKING_ERROR:
        return 1

    priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
    priority = check_priority_correctness(priority)
    if priority == CHECKING_ERROR:
        return 1

    progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
    progress = check_progress_correctness(progress)
    if progress == CHECKING_ERROR:
        return 1

    start = args.pop(ParserArgs.TASK_START.dest)
    start = check_time_format(start)
    if start == CHECKING_ERROR:
        return 1

    deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
    deadline = check_time_format(deadline)
    if deadline == CHECKING_ERROR:
        return 1

    tags = args.pop(ParserArgs.TASK_TAGS.dest)
    tags = check_tags_correctness(tags)
    if tags == CHECKING_ERROR:
        return 1

    reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
    reminder = check_reminder_format(reminder)
    if reminder == CHECKING_ERROR:
        return 1

    status = args.pop(ParserArgs.TASK_STATUS.dest)
    status = check_status_correctness(status)
    if status == CHECKING_ERROR:
        return 1

    try:
        lib_interface.edit_task(
            key=key,
            name=args.pop(ParserArgs.TASK_NEW_NAME.dest),
            description=args.pop(ParserArgs.TASK_DESCRIPTION.dest),
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
    except TaskError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('Task with key "{}" edited'.format(key))
        return 0


def _del_task(args, lib_interface) -> int:
    key = args.pop(ParserArgs.TASK_KEY.name)
    try:
        lib_interface.del_task(
            key=key,
            recursive=args.pop(ParserArgs.RECURSIVE.dest)
        )
    except TaskError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print('Task with key "{}" deleted'.format(key))
    return 0


# ===================================================
# private functions. Don't use outside this module! =
# ===================================================
def _get_parsers():
    """
    Init parser's attributes, create parsers and subparsers
    :return parser, active_sub_parser, where
            parser - main parser,
            active_sub_parser - current sub_parser which used in program
    """
    parser = FormattedParser(
        description=ParserArgs.DESCRIPTION)
    subparsers = parser.add_subparsers(
        dest=ParserArgs.TARGET.name,
        help=ParserArgs.TARGET.help)

    # create next level parsers for different targets
    active_sub_parser = None
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

    # check console args, create subparsers for necessary args
    if ParserArgs.USER.name in sys.argv:
        _create_user_subparsers(user_parser)
        active_sub_parser = user_parser

    elif ParserArgs.QUEUE.name in sys.argv:
        _create_queue_subparsers(queue_parser)
        active_sub_parser = queue_parser

    elif ParserArgs.TASK.name in sys.argv:
        _create_task_subparsers(task_parser)
        active_sub_parser = task_parser

    elif ParserArgs.PLAN.name in sys.argv:
        _create_plan_subparsers(plan_parser)
        active_sub_parser = plan_parser

    return parser, active_sub_parser


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
    add_subparsers.add_argument(
        dest=ParserArgs.NICKNAME.name,
        help=ParserArgs.NICKNAME.help)
    add_subparsers.add_argument(
        dest=ParserArgs.PASSWORD.name,
        help=ParserArgs.PASSWORD.help)

    # calistra user login <nickname> <password>
    login_subparsers = user_subparsers.add_parser(
        name=ParserArgs.LOGIN.name,
        help=ParserArgs.LOGIN.help)
    login_subparsers.add_argument(
        dest=ParserArgs.NICKNAME.name,
        help=ParserArgs.NICKNAME.help)
    login_subparsers.add_argument(
        dest=ParserArgs.PASSWORD.name,
        help=ParserArgs.PASSWORD.help)

    # calistra user logout (only for online user)
    user_subparsers.add_parser(
        name=ParserArgs.LOGOUT.name,
        help=ParserArgs.LOGOUT.help)

    # calistra user show
    user_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_USER_HELP)


# TODO: добавить документацию и опциональные параметры
def _create_queue_subparsers(queue_parser):
    queue_subparsers = queue_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.QUEUE_ACTION)

    # calistra queueshow_subparsers add
    add_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_QUEUE_HELP)

    # calistra queue add <name>
    add_subparsers.add_argument(
        dest=ParserArgs.QUEUE_NAME.name,
        help=ParserArgs.QUEUE_NAME.help)

    # calistra queue set
    edit_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_QUEUE_HELP)

    # calistra queue set <name>
    edit_subparsers.add_argument(
        dest=ParserArgs.QUEUE_NAME.name,
        help=ParserArgs.QUEUE_NAME.help)

    # calistra queue set <name> <new_name>
    edit_subparsers.add_argument(
        dest=ParserArgs.QUEUE_NEW_NAME.name,
        help=ParserArgs.QUEUE_NEW_NAME.help)

    # calistra queue del
    del_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DELETE_QUEUE_HELP)

    # calistra queue del <name>
    del_subparsers.add_argument(
        dest=ParserArgs.QUEUE_NAME.name,
        help=ParserArgs.QUEUE_NAME.help)

    del_subparsers.add_argument(
        ParserArgs.RECURSIVE.short,
        ParserArgs.RECURSIVE.long,
        dest=ParserArgs.RECURSIVE.dest,
        action="store_true",
        help=ParserArgs.RECURSIVE.help)

    # calistra queue show
    show_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_QUEUE_HELP,
    )

    show_args_group = show_subparsers.add_mutually_exclusive_group()
    show_args_group.description = 'kek'
    # calistra queue show [--name="NAME"]
    show_args_group.add_argument(
        ParserArgs.TASK_QUEUE.long,
        dest=ParserArgs.TASK_QUEUE.dest,
        help=ParserArgs.TASK_QUEUE.help
    )

    show_args_group.add_argument(
        ParserArgs.ALL.long,
        ParserArgs.ALL.short,
        dest=ParserArgs.ALL.dest,
        action="store_true",
        default=True,
        help=ParserArgs.ALL.help
    )


def _create_task_subparsers(task_parser):
    """Create subparsers for processing task's data
    :param task_parser
    :return None
    """
    task_subparsers = task_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.TASK_ACTION)

    # TODO: подумать над атрибутами task

    # calistra task add
    add_subparsers = task_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_TASK_HELP)

    # positional args for add_subparsers
    # calistra task add <name>
    add_subparsers.add_argument(
        dest=ParserArgs.TASK_NAME.name,
        help=ParserArgs.TASK_NAME.help)

    # calistra task add [--queue=<QUEUE>]
    add_subparsers.add_argument(
        ParserArgs.TASK_QUEUE.long,
        dest=ParserArgs.TASK_QUEUE.dest,
        default='inbox',
        help=ParserArgs.TASK_QUEUE.help)

    # add optional arguments
    __add_common_optional_task_args(add_subparsers)

    # calistra task set
    edit_subparsers = task_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_TASK_HELP)

    # positional args for edit_subparsers
    # calistra task set <TASK_KEY>
    edit_subparsers.add_argument(
        dest=ParserArgs.TASK_KEY.name,
        help=ParserArgs.TASK_KEY.help)

    # optional args for edit_subparsers
    # calistra task set --new_name=<NEW_NAME>
    edit_subparsers.add_argument(
        ParserArgs.TASK_NEW_NAME.long,
        dest=ParserArgs.TASK_NEW_NAME.dest,
        help=ParserArgs.TASK_NEW_NAME.help)

    # calistra task set --status=<STATUS>
    edit_subparsers.add_argument(
        ParserArgs.TASK_STATUS.long,
        dest=ParserArgs.TASK_STATUS.dest,
        help=ParserArgs.TASK_STATUS.help)

    __add_common_optional_task_args(edit_subparsers)

    # calistra task delete
    del_subparsers = task_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DELETE_TASK_HELP)

    # positional args for del_subparsers
    # calistra task del <TASK_KEY>
    del_subparsers.add_argument(
        dest=ParserArgs.TASK_KEY.name,
        help=ParserArgs.TASK_KEY.help)

    # optional args for del_subparsers
    # calistra task del [-r]
    del_subparsers.add_argument(
        ParserArgs.RECURSIVE.short,
        ParserArgs.RECURSIVE.long,
        dest=ParserArgs.RECURSIVE.dest,
        action="store_true",
        help=ParserArgs.RECURSIVE.help)

    # calistra task show
    task_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_TASK_HELP)


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
