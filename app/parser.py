"""This module have a Parser class for create console arguments parser
which parsing console args string

The following is a simple usage example:

    import sys
    import parser

    parser_ = parser.Parser(sys.argv)
    args_dict = parser_.get_args_dict()
"""
from argparse import ArgumentParser


class _ParserArgs:
    """Constants, which using in main parser as commands and settings for arguments"""
    DESCRIPTION = 'Calistra - task tracker'
    TARGET = 'target'
    TARGET_HELP = 'target for working'
    ACTION = 'action'
    ADD = 'add'
    DELETE = 'del'
    EDIT = 'edit'


class _UserArgs:
    """Constants, which represent user parser commands and settings"""
    USER = 'user'
    USER_HELP = 'working with user'
    USER_SUBPARSER_HELP = 'action with user'
    NICKNAME = 'nick'
    NICKNAME_HELP = "user's nickname"
    PASSWORD = 'pasw'
    PASSWORD_HELP = "user's password"
    ADD_USER_HELP = 'add new user'
    DELETE_USER_HELP = 'delete existing user'
    LOGIN = 'login'
    LOGIN_HELP = "login with nickname and password"


class _TaskArgs:
    """Constants, which represent task parser commands and settings"""
    TASK = 'task'
    TASK_HELP = 'working with tasks'
    ADD_TASK_HELP = 'add new task'
    DELETE_TASK_HELP = 'delete existing task'
    EDIT_TASK_HELP = 'edit task'
    TASK_SUBPARSER_HELP = 'work with task'


class Parser:
    """Object for parsing command line string into dictionary of args"""

    def __init__(self, console_args):
        """Init parser's attributes, create parsers and subparsers"""
        self.args = console_args
        self.parser = ArgumentParser(
            description=_ParserArgs.DESCRIPTION)
        subparsers = self.parser.add_subparsers(
            dest=_ParserArgs.TARGET,
            help=_ParserArgs.TARGET_HELP)

        # create next level parsers for different targets
        user_parser = subparsers.add_parser(
            name=_UserArgs.USER,
            help=_UserArgs.USER_HELP)
        task_parser = subparsers.add_parser(
            name=_TaskArgs.TASK,
            help=_TaskArgs.TASK_HELP)

        # check console args and create subparsers for necessary args
        if _UserArgs.USER in self.args:
            self._create_user_subparsers(user_parser)
            # save user parser as active target for show right error message
            self.active_target = user_parser
        elif _TaskArgs.TASK in self.args:
            self._create_task_subparsers(task_parser)
            # save target parser as active target for show right error message
            self.active_target = task_parser

    @staticmethod
    def _create_user_subparsers(user_parser):
        """Create subparsers for processing user's data
        :return: None
        """
        user_subparsers = user_parser.add_subparsers(
            dest=_ParserArgs.ACTION,
            help=_UserArgs.USER_SUBPARSER_HELP)

        # calistra user add <nickname> <password>
        add_subparsers = user_subparsers.add_parser(
            name=_ParserArgs.ADD,
            help=_UserArgs.ADD_USER_HELP)
        add_subparsers.add_argument(
            dest=_UserArgs.NICKNAME,
            help=_UserArgs.NICKNAME_HELP)
        add_subparsers.add_argument(
            dest=_UserArgs.PASSWORD,
            help=_UserArgs.PASSWORD_HELP)

        # calistra user login <nickname> <password>
        login_subparsers = user_subparsers.add_parser(
            name=_UserArgs.LOGIN,
            help=_UserArgs.LOGIN_HELP)
        login_subparsers.add_argument(
            dest=_UserArgs.NICKNAME,
            help=_UserArgs.NICKNAME_HELP)
        login_subparsers.add_argument(
            dest=_UserArgs.PASSWORD,
            help=_UserArgs.PASSWORD_HELP)

        # calistra user delete <nickname> <password>
        delete_subparsers = user_subparsers.add_parser(
            name=_ParserArgs.DELETE,
            help=_UserArgs.DELETE_USER_HELP)
        delete_subparsers.add_argument(
            dest=_UserArgs.NICKNAME,
            help=_UserArgs.NICKNAME_HELP)
        delete_subparsers.add_argument(
            dest=_UserArgs.PASSWORD,
            help=_UserArgs.PASSWORD_HELP)

    @staticmethod
    def _create_task_subparsers(task_parser):
        """
        Create subparsers for processing task's data
        :arg task_parser
        :return None
        """
        task_subparsers = task_parser.add_subparsers(
            dest=_ParserArgs.ACTION,
            help=_TaskArgs.TASK_SUBPARSER_HELP)

        # TODO: подумать над атрибутами task

        # calistra task add
        add_subparsers = task_subparsers.add_parser(
            name=_ParserArgs.ADD,
            help=_TaskArgs.ADD_TASK_HELP)

        # calistra task edit
        edit_subparsers = task_subparsers.add_parser(
            name=_ParserArgs.EDIT,
            help=_TaskArgs.EDIT_TASK_HELP)

        # calistra task delete
        delete_subparsers = task_subparsers.add_parser(
            name=_ParserArgs.DELETE,
            help=_TaskArgs.DELETE_TASK_HELP)

    def get_commands(self):
        """
        Return a dict of args and values:

        Example of console input:
            >> calistra user add IgorXXL 897897
            Namespace(action='add', nick='igorxxxl', pasw='8897', target='user')

        :return dict
        """
        return self.parser.parse_args()

    def show_usage(self, stream, level=1):
        """
        Show help message in case incorrect user's input

        Keyword arguments:
            :arg stream -- output stream
            :arg level -- subparsers level (default 1)

        :return: None
        """
        if level == 1:
            self.parser.print_help(stream)
        elif level == 2:
            self.active_target.print_help(stream)
