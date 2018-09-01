"""
This module contains functions for work with program's instances,
recognize user's console input and call library's functions for
work with program's entities
"""

import sys
from app.formatted_argparse import FormattedParser
from app.parser_args import ParserArgs


def get_parsers():
    """
    Init parser's attributes, create parsers and subparsers
    :return parser - main parser
    """
    parser = FormattedParser(
        description=ParserArgs.DESCRIPTION)
    subparsers = parser.add_subparsers(
        dest=ParserArgs.TARGET.name,
        help=ParserArgs.TARGET.help)

    # for parsing configuration settings
    config_parser = subparsers.add_parser(
        name=ParserArgs.CONFIG.name,
        help=ParserArgs.CONFIG.help
    )

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

    updater_parser = subparsers.add_parser(
        name=ParserArgs.UPDATE.name,
        help=ParserArgs.UPDATE.help
    )

    # check console args, create subparsers for necessary args
    if ParserArgs.CONFIG.name in sys.argv:
        FormattedParser.active_sub_parser = config_parser
        _create_config_subparsers(config_parser)

    elif ParserArgs.USER.name in sys.argv:
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

    elif ParserArgs.UPDATE.name in sys.argv:
        FormattedParser.active_sub_parser = updater_parser

    return parser


# ===============================================================
# private functions. Don't use outside this module, as possible! =
# ===============================================================
def _create_config_subparsers(config_parser):
    """
    Create subparsers for processing configuration data
    :param config_parser: high level parser
    :return: None
    """
    config_subparsers = config_parser.add_subparsers(
        dest=ParserArgs.ACTION,
        help=ParserArgs.CONFIG_ACTION
    )

    # calistra config set
    set_subparsers = config_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_CONFIG_HELP
    )

    # calistra config reset
    reset_subparsers = config_subparsers.add_parser(
        name=ParserArgs.RESET,
        help=ParserArgs.CONFIG_RESET_HELP
    )

    if ParserArgs.SET in sys.argv:
        # calistra config set <CONFIG_TYPE>
        type_subparsers = set_subparsers.add_subparsers(
            dest=ParserArgs.CONFIG_TYPE.name,
            help=ParserArgs.CONFIG_TYPE.help
        )

        settings_subparsers = type_subparsers.add_parser(
            name=ParserArgs.SETTINGS.name,
            help=ParserArgs.SETTINGS.help,
        )

        logger_subparsers = type_subparsers.add_parser(
            name=ParserArgs.LOGGER.name,
            help=ParserArgs.LOGGER.help
        )
        if ParserArgs.SETTINGS.name in sys.argv:

            # calistra config set settings --path=<PATH_TO_DATA>
            settings_subparsers.add_argument(
                ParserArgs.STORAGE_PATH.long,
                dest=ParserArgs.STORAGE_PATH.dest,
                help=ParserArgs.STORAGE_PATH.help
            )

            FormattedParser.active_sub_parser = settings_subparsers

        elif ParserArgs.LOGGER.name in sys.argv:

            # calistra config set logger --level=<LOGGER_LEVEL>
            logger_subparsers.add_argument(
                ParserArgs.LOGGER_LEVEL.long,
                dest=ParserArgs.LOGGER_LEVEL.dest,
                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
                         'NOTSET'],
                help=ParserArgs.LOGGER_LEVEL.help
            )

            # calistra config set logger --path=<PATH_TO_LOG_FILE>
            logger_subparsers.add_argument(
                ParserArgs.LOG_FILE_PATH.long,
                dest=ParserArgs.LOG_FILE_PATH.dest,
                help=ParserArgs.LOG_FILE_PATH.help
            )

            # calistra config set logger --enabled=<
            logger_subparsers.add_argument(
                ParserArgs.ENABLED_LOGGER.long,
                dest=ParserArgs.ENABLED_LOGGER.dest,
                choices=['True', 'False'],
                help=ParserArgs.ENABLED_LOGGER.help
            )

            FormattedParser.active_sub_parser = logger_subparsers

        else:
            set_subparsers.error('Type of configurated object is needed')

    elif ParserArgs.RESET in sys.argv:
        # calistra config reset <CONFIG_TYPE>
        reset_subparsers.add_argument(
            dest=ParserArgs.CONFIG_TYPE.name,
            help=ParserArgs.CONFIG_TYPE.help,
            choices=[ParserArgs.SETTINGS.name, ParserArgs.LOGGER.name]
        )
        FormattedParser.active_sub_parser = reset_subparsers


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
        show_subparsers.add_argument(
            ParserArgs.LONG.short,
            ParserArgs.LONG.long,
            action=ParserArgs.__STORE_TRUE__,
            dest=ParserArgs.LONG.dest,
            help=ParserArgs.LONG.help
        )

        show_subparsers.add_argument(
            ParserArgs.SORT_BY.long,
            dest=ParserArgs.SORT_BY.dest,
            choices=ParserArgs.SORT_BY_CHOICES,
            help=ParserArgs.SORT_BY.help
        )
        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.LOGOUT.name in sys.argv:
        FormattedParser.active_sub_parser = logout_subparsers


def _create_queue_subparsers(queue_parser):
    """
    Create sub parser for processing queue data
    :param queue_parser: level highier parser
    :return: None
    """
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

    find_subparsers = queue_subparsers.add_parser(
        name=ParserArgs.FIND,
        help=ParserArgs.FIND_QUEUE_HELP
    )

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

        show_subparsers.add_argument(
            ParserArgs.SORT_BY.long,
            dest=ParserArgs.SORT_BY.dest,
            choices=ParserArgs.SORT_BY_CHOICES,
            help=ParserArgs.SORT_BY.help
        )

        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.FIND in sys.argv:
        find_subparsers.add_argument(
            ParserArgs.QUEUE_NAME.name,
            help=ParserArgs.QUEUE_NAME.help
        )
        FormattedParser.active_sub_parser = find_subparsers


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

    # calistra task find
    find_subparsers = task_subparsers.add_parser(
        name=ParserArgs.FIND,
        help=ParserArgs.FIND_TASK_HELP
    )

    activate_subparsers = task_subparsers.add_parser(
        name=ParserArgs.ACTIVATE,
        help=ParserArgs.ACTIVATE_TASK_HELP
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
        # calistra task show <key>
        show_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        # calistra task show --long
        show_subparsers.add_argument(
            ParserArgs.LONG.short,
            ParserArgs.LONG.long,
            action=ParserArgs.__STORE_TRUE__,
            dest=ParserArgs.LONG.dest,
            help=ParserArgs.LONG.help
        )
        FormattedParser.active_sub_parser = show_subparsers

    elif ParserArgs.FIND in sys.argv:
        # calistra task find --name=<NAME>
        args_group = find_subparsers.add_mutually_exclusive_group()
        args_group.add_argument(
            ParserArgs.TASK_NAME_OPTIONAL.long,
            dest=ParserArgs.TASK_NAME_OPTIONAL.dest,
            help=ParserArgs.TASK_NAME_OPTIONAL.help)

        # calistra task find --tag=<TAG>
        args_group.add_argument(
            ParserArgs.TASK_TAGS.long,
            dest=ParserArgs.TASK_TAGS.dest,
            help=ParserArgs.FIND_BY_TAG_HELP
        )
        FormattedParser.active_sub_parser = find_subparsers

    elif ParserArgs.ACTIVATE in sys.argv:
        activate_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help)

        FormattedParser.active_sub_parser = activate_subparsers


def __add_common_optional_task_args(action_subparser):
    """
    :param action_subparser: subparser of a certain action with a task
    :return: None
    """
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

    # calistra task <action> [--related=<RELATED>]
    action_subparser.add_argument(
        ParserArgs.TASK_RELATED.long,
        dest=ParserArgs.TASK_RELATED.dest,
        help=ParserArgs.TASK_RELATED.help)

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

    add_subparsers = plan_subparsers.add_parser(
        name=ParserArgs.ADD,
        help=ParserArgs.ADD_PLAN
    )

    edit_subparsers = plan_subparsers.add_parser(
        name=ParserArgs.SET,
        help=ParserArgs.SET_PLAN
    )

    show_suparsers = plan_subparsers.add_parser(
        name=ParserArgs.SHOW,
        help=ParserArgs.SHOW_PLAN_HELP
    )

    delete_subparsers = plan_subparsers.add_parser(
        name=ParserArgs.DELETE,
        help=ParserArgs.DEL_PLAN
    )

    if ParserArgs.ADD in sys.argv:
        add_subparsers.add_argument(
            ParserArgs.PLAN_NAME.name,
            help=ParserArgs.PLAN_NAME.help
        )

        add_subparsers.add_argument(
            ParserArgs.PLAN_PERIOD.name,
            help=ParserArgs.PLAN_PERIOD.help
        )

        add_subparsers.add_argument(
            ParserArgs.PLAN_ACTIVATION_TIME.name,
            help=ParserArgs.PLAN_ACTIVATION_TIME.help
        )

        add_subparsers.add_argument(
            ParserArgs.TASK_REMINDER.long,
            dest=ParserArgs.TASK_REMINDER.dest,
            help=ParserArgs.TASK_REMINDER.help
        )

        FormattedParser.active_sub_parser = add_subparsers

    elif ParserArgs.SET in sys.argv:
        edit_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help
        )

        edit_subparsers.add_argument(
            ParserArgs.PLAN_NAME_OPTIONAL.long,
            dest=ParserArgs.PLAN_NAME_OPTIONAL.dest,
            help=ParserArgs.PLAN_NAME_OPTIONAL.help
        )

        edit_subparsers.add_argument(
            ParserArgs.PLAN_ACTIVATION_TIME_OPTIONAL.long,
            dest=ParserArgs.PLAN_ACTIVATION_TIME_OPTIONAL.dest,
            help=ParserArgs.PLAN_ACTIVATION_TIME_OPTIONAL.help
        )

        edit_subparsers.add_argument(
            ParserArgs.PLAN_PERIOD_OPTIONAL.long,
            dest=ParserArgs.PLAN_PERIOD_OPTIONAL.dest,
            help=ParserArgs.PLAN_PERIOD_OPTIONAL.help
        )

        edit_subparsers.add_argument(
            ParserArgs.TASK_REMINDER.long,
            dest=ParserArgs.TASK_REMINDER.dest,
            help=ParserArgs.TASK_REMINDER.help
        )

        FormattedParser.active_sub_parser = edit_subparsers

    elif ParserArgs.SHOW in sys.argv:
        FormattedParser.active_sub_parser = show_suparsers

    elif ParserArgs.DELETE in sys.argv:
        delete_subparsers.add_argument(
            ParserArgs.KEY.name,
            help=ParserArgs.KEY.help
        )

        FormattedParser.active_sub_parser = delete_subparsers


def _create_notification_subparsers(notification_parser):
    """
    Create subparsers for processing notifications
    :param notification_parser: high level parser
    :return: None
    """
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
