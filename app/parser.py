"""This module have a Parser class for processing users's console input"""
from argparse import ArgumentParser


class ParserConstants:
    """Constants, which represent main parser commands and settings"""
    DESCRIPTION = 'Calistra - task tracker'
    TARGET = 'target'
    TARGET_HELP = 'target for working'
    ACTIVE_TARGET = None
    ACTION = 'action'
    ADD = 'add'
    DELETE = 'del'
    EDIT = 'edit'


class UserParserConstants:
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


class TaskParserConstants:
    """Constants, which represent task parser commands and settings"""
    TASK = 'task'
    TASK_HELP = 'working with tasks'
    ADD_TASK_HELP = 'add new task'
    DELETE_TASK_HELP = 'delete existing task'
    EDIT_TASK_HELP = 'edit task'
    TASK_SUBPARSER_HELP = 'work with task'


class Parser:
    """Class for processing console input"""

    def __init__(self, console_args):
        """Init parser's attributes and create parsers"""
        self.args = console_args
        self.parser = ArgumentParser(
            description=ParserConstants.DESCRIPTION)
        subparsers = self.parser.add_subparsers(
            dest=ParserConstants.TARGET,
            help=ParserConstants.TARGET_HELP)

        # create next level parsers for different targets
        user_parser = subparsers.add_parser(
            name=UserParserConstants.USER,
            help=UserParserConstants.USER_HELP)
        task_parser = subparsers.add_parser(
            name=TaskParserConstants.TASK,
            help=TaskParserConstants.TASK_HELP)

        # check console args and create subparsers for necessary args
        if UserParserConstants.USER in self.args:
            self._create_user_subparsers(user_parser)
            # save user parser as active target for show right error message
            self.active_target = user_parser
        elif TaskParserConstants.TASK in self.args:
            self._create_task_subparsers(task_parser)
            # save target parser as active target for show right error message
            self.active_target = task_parser

    @staticmethod
    def _create_user_subparsers(user_parser):
        """Create subparsers for processing user's data"""
        user_subparsers = user_parser.add_subparsers(
            dest=ParserConstants.ACTION,
            help=UserParserConstants.USER_SUBPARSER_HELP)

        # calistra user add <nickname> <password>
        add_subparsers = user_subparsers.add_parser(
            name=ParserConstants.ADD,
            help=UserParserConstants.ADD_USER_HELP)
        add_subparsers.add_argument(
            dest=UserParserConstants.NICKNAME,
            help=UserParserConstants.NICKNAME_HELP)
        add_subparsers.add_argument(
            dest=UserParserConstants.PASSWORD,
            help=UserParserConstants.PASSWORD_HELP)

        # calistra user login <nickname> <password>
        login_subparsers = user_subparsers.add_parser(
            name=UserParserConstants.LOGIN,
            help=UserParserConstants.LOGIN_HELP)
        login_subparsers.add_argument(
            dest=UserParserConstants.NICKNAME,
            help=UserParserConstants.NICKNAME_HELP)
        login_subparsers.add_argument(
            dest=UserParserConstants.PASSWORD,
            help=UserParserConstants.PASSWORD_HELP)

        # calistra user delete <nickname> <password>
        delete_subparsers = user_subparsers.add_parser(
            name=ParserConstants.DELETE,
            help=UserParserConstants.DELETE_USER_HELP)
        delete_subparsers.add_argument(
            dest=UserParserConstants.NICKNAME,
            help=UserParserConstants.NICKNAME_HELP)
        delete_subparsers.add_argument(
            dest=UserParserConstants.PASSWORD,
            help=UserParserConstants.PASSWORD_HELP)

    @staticmethod
    def _create_task_subparsers(task_parser):
        """Create subparsers for processing task's data"""
        task_subparsers = task_parser.add_subparsers(
            dest=ParserConstants.ACTION,
            help=TaskParserConstants.TASK_SUBPARSER_HELP)

        # TODO: подумать над атрибутами task

        # calistra task add
        add_subparsers = task_subparsers.add_parser(
            name=ParserConstants.ADD,
            help=TaskParserConstants.ADD_TASK_HELP)

        # calistra task edit
        edit_subparsers = task_subparsers.add_parser(
            name=ParserConstants.EDIT,
            help=TaskParserConstants.EDIT_TASK_HELP)

        # calistra task delete
        delete_subparsers = task_subparsers.add_parser(
            name=ParserConstants.DELETE,
            help=TaskParserConstants.DELETE_TASK_HELP)

    def get_args_dict(self):
        """Create a dict of args and values"""
        return vars(self.parser.parse_args())

    def show_usage(self, dest, level=1):
        """
        Show help message in case incorrect user's input
        dest: output stream
        level: subparsers level
        """
        if level == 1:
            self.parser.print_help(dest)
        elif level == 2:
            self.active_target.print_help(dest)
