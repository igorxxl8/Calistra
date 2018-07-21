import argparse as ap


class Parser:
    """Класс для обработки консольного ввода от пользователя."""
    # константы, использующиеся парсером
    DESCRIPTION = 'Calistra - task tracker'
    NICKNAME = 'nick'
    NICKNAME_HELP = "user's nickname"
    PASSWORD = 'pasw'
    PASSWORD_HELP = "user's password"
    SUBPARSERS_HELP = 'target'
    USER = 'user'
    USER_HELP = 'working with user'
    USER_SUBPARSER_HELP = 'operation with user'
    ADD = 'add'
    ADD_USER_HELP = 'add new user'
    ADD_TASK_HELP = 'add new task'
    LOGIN = 'login'
    LOGIN_HELP = "login with nickname and password"
    DELETE = 'del'
    DELETE_USER_HELP = 'delete existing user'
    DELETE_TASK_HELP = 'delete existing task'
    TASK = 'task'
    TASK_HELP = 'working with tasks'
    EDIT = 'edit'
    EDIT_TASK_HELP = 'edit task'
    TASK_SUBPARSER_HELP = 'work with task'

    def __init__(self, console_args):
        self.args = console_args
        self.parser = ap.ArgumentParser(
            argument_default=ap.SUPPRESS,
            description=Parser.DESCRIPTION
        )
        self.subparsers = self.parser.add_subparsers(
            help=Parser.SUBPARSERS_HELP
        )

        if len(self.args) > 1:
            # субпарсеры обработки данных о пользователе
            user_parser = self.subparsers.add_parser(
                name=Parser.USER,
                help=Parser.USER_HELP
            )
            task_parser = self.subparsers.add_parser(
                name=Parser.TASK,
                help=Parser.TASK_HELP
            )
            if self.args[1] == Parser.USER:
                user_subparsers = user_parser.add_subparsers(
                    help=Parser.USER_SUBPARSER_HELP
                )
                register_subparsers = user_subparsers.add_parser(
                    name=Parser.ADD,
                    help=Parser.ADD_USER_HELP
                )
                register_subparsers.add_argument(
                    dest=Parser.NICKNAME,
                    help=Parser.NICKNAME_HELP
                )
                register_subparsers.add_argument(
                    dest=Parser.PASSWORD,
                    help=Parser.PASSWORD_HELP
                )
                login_subparsers = user_subparsers.add_parser(
                    name=Parser.LOGIN,
                    help=Parser.LOGIN_HELP
                )
                login_subparsers.add_argument(
                    dest=Parser.NICKNAME,
                    help=Parser.NICKNAME_HELP
                )
                login_subparsers.add_argument(
                    dest=Parser.PASSWORD,
                    help=Parser.PASSWORD_HELP
                )
                delete_subparsers = user_subparsers.add_parser(
                    name=Parser.DELETE,
                    help=Parser.DELETE_USER_HELP
                )
                delete_subparsers.add_argument(
                    dest=Parser.NICKNAME,
                    help=Parser.NICKNAME_HELP
                )
                delete_subparsers.add_argument(
                    dest=Parser.PASSWORD,
                    help=Parser.PASSWORD_HELP
                )

            elif self.args[1] == Parser.TASK:
                # субпарсеры для обработки данных о задачах
                task_subparsers = task_parser.add_subparsers(
                    help=Parser.TASK_SUBPARSER_HELP
                )
                crt_subparsers = task_subparsers.add_parser(
                    name=Parser.ADD,
                    help=Parser.ADD_TASK_HELP
                )
                edit_subparsers = task_subparsers.add_parser(
                    name=Parser.EDIT,
                    help=Parser.EDIT_TASK_HELP
                )
                del_subparsers = task_subparsers.add_parser(
                    name=Parser.DELETE,
                    help=Parser.DELETE_TASK_HELP
                )

    def parse(self):
        return self.parser.parse_args()
