"""
This module contains functions for work program's instances, recognize user's
console input and call library's functions for work with program's entities
"""

# TODO: 1) write docstring for parser module
# TODO: 2) continue write parser

from argparse import ArgumentParser
from collections import namedtuple
from user import *
import sys


def run():
    """
    Start program
    :return: int - exit code
    """
    # sub_parser define message which print in case lack of necessary arguments
    parser, sub_parser = _get_parser()
    args = parser.parse_args()

    # check target argument
    if not args.target:
        parser.print_help(sys.stderr)
        return 1

    # check action argument
    if not args.action:
        sub_parser.print_help(sys.stderr)
        return 1

    if args.target == _ParserArgs.USER.name:
        user_handler(args)

    elif args.target == _ParserArgs.TASK.name:
        task_handler(args)


# =================================================
# functions for work with user's account instance =
# =================================================
def user_handler(args):
    # TODO: сделать библиотечную часть логики пользователей
    """
    This procedure recognizes the action that must be performed
    on the user account and delegates its implementation to the
    required procedure.
    :arg args -- contains command and info about user
    :return: None
    """
    if args.action == _ParserArgs.ADD:
        _add_user(args)
    elif args.action == _ParserArgs.DELETE:
        _delete_user()
    elif args.action == _ParserArgs.LOGIN.name:
        _login(args)
    elif args.action == _ParserArgs.LOGOUT.name:
        _logout()


def _add_user(console_args):
    # TODO: сделать лучшее отображение
    storage = UserWrapperStorage()
    user = UserWrapper(
        nick=console_args.nick,
        password=console_args.pasw
    )
    try:
        storage.save_user(user)
    except SaveUserError as e:
        print(e.message, file=sys.stderr)
    else:
        print("User {} successfully created".format(console_args.nick))


def _login(console_args):
    storage = UserWrapperStorage()
    controller = UserWrapperController(storage)
    try:
        controller.login_user(console_args.nick, console_args.pasw)
    except LoginError as e:
        print(e.message, file=sys.stderr)
    else:
        print("User {} now is online".format(console_args.nick))


def _logout():
    storage = UserWrapperStorage()
    controller = UserWrapperController(storage)
    try:
        controller.logout_user()
    except LogoutError as e:
        print(e.message, file=sys.stderr)
    else:
        print("All users now offline")


def _delete_user():
    # TODO: подумать над необходимостью метода удаление пользователя
    """
    This procedure delete current online user
    :return: None
    """
    pass


# =================================================
# functions for work with single task instance    =
# =================================================
def task_handler(task_attr):
    pass


def _add_task():
    pass


def _del_task():
    pass


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
    DELETE = 'del'
    SET = 'set'

    # Constants, which represent user parser commands and settings
    USER = Argument(name='user', help='work with user\'s account')
    USER_ACTION = 'action with user'
    LOGIN = Argument(name='login', help='login with nickname and password')
    LOGOUT = Argument(name='logout', help='log out of user\'s session')
    NICKNAME = Argument(name='nick', help='user\'s nickname')
    PASSWORD = Argument(name='pasw', help='user\'s password')
    ADD_USER_HELP = 'add new user'
    DELETE_USER_HELP = 'delete current user'
    EDIT_USER_HELP = 'edit current user'

    # Constants, which represent task parser commands and settings
    TASK = Argument(name='task', help='work with single task')
    TASK_ACTION = 'action with task'
    ADD_TASK_HELP = 'add new task'
    DELETE_TASK_HELP = 'delete existing task'
    EDIT_TASK_HELP = 'edit task'

    # Constants, which represent plan parser commands and settings

    PLAN = Argument(name='plan', help='work with plans')
    PLAN_ACTION = 'action with plans'


# ===================================================
# private functions. Don't use outside this module! =
# ===================================================
def _get_parser():
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

    # calistra user delete <password> (only for online user)
    delete_subparsers = user_subparsers.add_parser(
        name=_ParserArgs.DELETE,
        help=_ParserArgs.DELETE_USER_HELP)
    delete_subparsers.add_argument(
        dest=_ParserArgs.PASSWORD.name,
        help=_ParserArgs.PASSWORD.help)


def _create_task_subparsers(task_parser):
    """
    Create subparsers for processing task's data
    :arg task_parser
    :return None
    """
    task_subparsers = task_parser.add_subparsers(
        dest=_ParserArgs.ACTION,
        help=_ParserArgs.TASK_ACTION)

    # TODO: подумать над атрибутами task

    # calistra task add
    add_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.ADD,
        help=_ParserArgs.ADD_TASK_HELP)

    # calistra task edit
    edit_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.SET,
        help=_ParserArgs.EDIT_TASK_HELP)

    # calistra task delete
    delete_subparsers = task_subparsers.add_parser(
        name=_ParserArgs.DELETE,
        help=_ParserArgs.DELETE_TASK_HELP)


def _create_plan_subparsers(plan_parser):
    """
        Create subparsers for processing plan's data
        :arg plan_parser
        :return None
    """
    plan_subparsers = plan_parser.add_subparsers(
        dest=_ParserArgs.ACTION,
        help=_ParserArgs.PLAN_ACTION
    )
