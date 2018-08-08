"""
This module contains functions for work with program's instances,
recognize user's console input and call library's functions for
work with program's entities
"""

# TODO: 1) write docstring for parser module
# TODO: 2) continue write parser
import sys
import os
from argparse import ArgumentParser
from collections import namedtuple
from app.user_wrapper import (
    UserWrapper,
    UserWrapperStorage,
    UserWrapperController,
    LoginError,
    LogoutError,
    SaveUserError
)

try:
    from lib.calistra_lib.library_interface.interface import Interface
except ImportError:
    from calistra_lib.library_interface.interface import Interface


FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
TASKS_FILE = os.path.join(FOLDER, 'tasks.json')
USERS_FILE = os.path.join(FOLDER, 'users.json')
AUTH_FILE = os.path.join(FOLDER, 'auth.json')
ONLINE = os.path.join(FOLDER, 'online_user.json')


def run() -> int:
    """
    Start program
    :return: int - exit code
    """
    # sub_parser define message which print in case lack of necessary arguments
    parser, sub_parser = _get_parsers()
    args_dict = vars(parser.parse_args())

    target = args_dict.pop(_ParserArgs.TARGET.name)
    # check target argument
    if not target:
        parser.print_help(sys.stderr)
        return 1

    # check action argument
    action = args_dict.pop(_ParserArgs.ACTION)
    if not action:
        sub_parser.print_help(sys.stderr)
        return 1

    users_wrapper_storage = UserWrapperStorage(AUTH_FILE, ONLINE)
    online_user = users_wrapper_storage.get_online_user()
    if not online_user:
        library_interface = Interface(None, USERS_FILE, TASKS_FILE)
    else:
        library_interface = Interface(online_user.nick, USERS_FILE, TASKS_FILE)

    # check that target is user and do action with it
    if target == _ParserArgs.USER.name:
        if action == _ParserArgs.ADD:
            return _add_user(
                args_dict=args_dict,
                users_storage=users_wrapper_storage,
                library_interface=library_interface
            )

        if action == _ParserArgs.LOGIN.name:
            return _login(args_dict, users_wrapper_storage)
        if action == _ParserArgs.LOGOUT.name:
            return _logout(users_wrapper_storage)
        if action == _ParserArgs.SHOW:
            return _show_users(users_wrapper_storage)

    # check that target is task and do action with it
    if target == _ParserArgs.TASK.name:
        if action == _ParserArgs.ADD:
            pass

    # check that target is plan and do action with it
    if target == _ParserArgs.PLAN.name:
        if action == _ParserArgs.ADD:
            pass


# =================================================
# functions for work with user's account instance =
# =================================================
def _add_user(args_dict, users_storage, library_interface: Interface) -> int:
    nick = args_dict.pop(_ParserArgs.NICKNAME.name)
    password = args_dict.pop(_ParserArgs.PASSWORD.name)
    try:
        users_storage.add_user(nick, password)
    except SaveUserError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        library_interface.add_user(nick)
        print("User {} successfully created".format(nick))
        return 0


def _login(args_dict, users_storage) -> int:
    controller = UserWrapperController(users_storage)
    user = UserWrapper(
        nick=args_dict.pop(_ParserArgs.NICKNAME.name),
        password=args_dict.pop(_ParserArgs.PASSWORD.name)
    )
    try:
        controller.login(user)
    except LoginError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print("User {} now is online".format(user.nick))
        return 0


def _logout(users_storage) -> int:
    controller = UserWrapperController(users_storage)
    try:
        controller.logout()
    except LogoutError as e:
        print(e.message, file=sys.stderr)
        return 1
    else:
        print("All users now offline")
        return 0


def _show_users(storage) -> int:
    for user in storage.users:
        print('{}'.format(user.nick))
    return 0


# =====================================================
# Private class. Don't use it outside this module!    =
# =====================================================
class _ParserArgs:
    """Constants, which using in parser as commands and
    settings for arguments
    """

    # tuple for represent arguments
    Argument = namedtuple('Argument', ['name', 'help'])

    # main parser's arguments
    DESCRIPTION = 'Calistra - task tracker'
    TARGET = Argument(name='target',
                      help='select a target to work with')
    ACTION = 'action'
    ADD = 'add'
    SET = 'set'
    SHOW = 'show'
    DELETE = 'del'

    # Constants, which represent user parser commands and settings
    USER = Argument(name='user', help='work with user\'s account')
    USER_ACTION = 'action with user'
    LOGIN = Argument(name='login', help='login with nickname and password')
    LOGOUT = Argument(name='logout', help='log out of user\'s session')
    NICKNAME = Argument(name='nick', help='user\'s nickname')
    PASSWORD = Argument(name='pasw', help='user\'s password')
    ADD_USER_HELP = 'add new user'
    EDIT_USER_HELP = 'edit current user'
    SHOW_USER_HELP = 'show all user'

    # Constants, which represent task parser commands and settings
    TASK = Argument(name='task', help='work with single task')
    TASK_ACTION = 'action with task'
    ADD_TASK_HELP = 'add new task'
    DELETE_TASK_HELP = 'delete existing task'
    EDIT_TASK_HELP = 'edit task'
    SHOW_TASK_HELP = 'show user\'s tasks'
    TASK_NAME = Argument(name='name', help='name for task')

    # Constants, which represent plan parser commands and settings

    PLAN = Argument(name='plan', help='work with plans')
    PLAN_ACTION = 'action with plans'


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
    parser = ArgumentParser(
        description=_ParserArgs.DESCRIPTION)
    subparsers = parser.add_subparsers(
        dest=_ParserArgs.TARGET.name,
        help=_ParserArgs.TARGET.help)

    # create next level parsers for different targets
    active_sub_parser = None
    user_parser = subparsers.add_parser(
        name=_ParserArgs.USER.name,
        help=_ParserArgs.USER.help
    )

    task_parser = subparsers.add_parser(
        name=_ParserArgs.TASK.name,
        help=_ParserArgs.TASK.help
    )

    plan_parser = subparsers.add_parser(
        name=_ParserArgs.PLAN.name,
        help=_ParserArgs.PLAN.help
    )

    # check console args, create subparsers for necessary args
    if _ParserArgs.USER.name in sys.argv:
        _create_user_subparsers(user_parser)
        active_sub_parser = user_parser
    elif _ParserArgs.TASK.name in sys.argv:
        _create_task_subparsers(task_parser)
        active_sub_parser = task_parser

    elif _ParserArgs.PLAN.name in sys.argv:
        _create_plan_subparsers(plan_parser)
        active_sub_parser = plan_parser

    return parser, active_sub_parser


def _create_user_subparsers(user_parser):
    """
    Create subparsers for processing user's data
    :return: None
    """
    user_subparsers = user_parser.add_subparsers(
        dest=_ParserArgs.ACTION,
        help=_ParserArgs.USER_ACTION)

    # calistra user add <nickname> <password>
    add_subparsers = user_subparsers.add_parser(
        name=_ParserArgs.ADD,
        help=_ParserArgs.ADD_USER_HELP)
    add_subparsers.add_argument(
        dest=_ParserArgs.NICKNAME.name,
        help=_ParserArgs.NICKNAME.help)
    add_subparsers.add_argument(
        dest=_ParserArgs.PASSWORD.name,
        help=_ParserArgs.PASSWORD.help)

    # calistra user login <nickname> <password>
    login_subparsers = user_subparsers.add_parser(
        name=_ParserArgs.LOGIN.name,
        help=_ParserArgs.LOGIN.help)
    login_subparsers.add_argument(
        dest=_ParserArgs.NICKNAME.name,
        help=_ParserArgs.NICKNAME.help)
    login_subparsers.add_argument(
        dest=_ParserArgs.PASSWORD.name,
        help=_ParserArgs.PASSWORD.help)

    # calistra user logout (only for online user)
    user_subparsers.add_parser(
        name=_ParserArgs.LOGOUT.name,
        help=_ParserArgs.LOGOUT.help
    )

    # calistra user show
    user_subparsers.add_parser(
        name=_ParserArgs.SHOW,
        help=_ParserArgs.SHOW_USER_HELP
    )


def _create_task_subparsers(task_parser):
    """
    Create subparsers for processing task's data
    :param task_parser
    :return None
    """
    task_subparsers = task_parser.add_subparsers(
        dest=_ParserArgs.ACTION,
        help=_ParserArgs.TASK_ACTION)

    # TODO: подумать над атрибутами task

    # calistra task add
    add_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.ADD,
        help=_ParserArgs.ADD_TASK_HELP
    )

    add_subparsers.add_argument(
        dest=_ParserArgs.TASK_NAME.name,
        help=_ParserArgs.TASK_NAME.help
    )

    # calistra task edit
    edit_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.SET,
        help=_ParserArgs.EDIT_TASK_HELP
    )

    # calistra task delete
    delete_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.DELETE,
        help=_ParserArgs.DELETE_TASK_HELP
    )

    # calistra task show
    task_subparsers.add_parser(
        name=_ParserArgs.SHOW,
        help=_ParserArgs.SHOW_TASK_HELP
    )


def _create_plan_subparsers(plan_parser):
    """
        Create subparsers for processing plan's data
        :param plan_parser
        :return None
    """
    plan_subparsers = plan_parser.add_subparsers(
        dest=_ParserArgs.ACTION,
        help=_ParserArgs.PLAN_ACTION
    )
