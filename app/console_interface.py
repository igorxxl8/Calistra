import os
import sys
import uuid

from app.configuration import Files, Configuration
from app.command_parser import get_parsers
from app.formatted_argparse import FormattedParser
from app.help_functions import *
from app.parser_args import ParserArgs
from app.printer import Printer
from app.user_wrapper import (
    UserWrapperStorage,
    UserWrapperController,
    LoginError,
    LogoutError,
    SaveUserError
)
from calistra_lib.exceptions.base_exception import AppError
from calistra_lib.interface import Interface
from calistra_lib.logger import (
    log_cli,
    get_logger,
    set_logger_config_file,
    set_logger_enabled
)
from calistra_lib.plan.json_plan_storage import JsonPlanStorage
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.queue.json_queue_storage import JsonQueueStorage
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.task.json_task_storage import JsonTaskStorage
from calistra_lib.task.task import TaskStatus
from calistra_lib.task.task_controller import TaskController
from calistra_lib.user.json_user_storage import JsonUserStorage
from calistra_lib.user.user_controller import UserController

ERROR_CODE = 1
TASK_KEY_BYTES = 8
QUEUE_KEY_BYTES = 4
PLAN_KEY_BYTES = 6


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
    # check settings
    Configuration.apply_settings()
    set_logger_enabled(Configuration.is_logger_enabled())

    # check for files and create it if they missed
    check_program_data_files(Files.FOLDER, Files.FILES)

    # set logging configuration
    if os.path.exists(Files.LOG_CONFIG):
        set_logger_config_file(Files.LOG_CONFIG)
    else:
        set_logger_config_file(Files.DEFAULT_LOG_CONFIG_FILE)

    # create loggers and
    cli_logger = get_logger()
    cli_logger.info('Start program.')

    # load data from storage and create entities controllers
    users_wrapper_storage = UserWrapperStorage(Files.AUTH_FILE, Files.ONLINE)

    queue_storage = JsonQueueStorage(Files.QUEUES_FILE)
    queue_controller = QueueController(queue_storage)

    task_storage = JsonTaskStorage(Files.TASKS_FILE)
    task_controller = TaskController(task_storage)

    user_storage = JsonUserStorage(Files.USERS_FILE)
    user_controller = UserController(user_storage)

    plan_storage = JsonPlanStorage(Files.PLANS_FILE)
    plan_controller = PlanController(plan_storage)

    # init library interface
    library = Interface(users_wrapper_storage.online_user, queue_controller,
                        user_controller, task_controller, plan_controller)

    # update reminders deadlines queue and other
    library.update_all()
    _show_new_messages(library)

    parser = get_parsers()
    args = vars(parser.parse_args())
    cli_logger.debug('Console args: {}'.format(args))

    # check that target is defined
    target = args.pop(ParserArgs.TARGET.name)
    if target is None:
        parser.error('target is required', need_to_exit=False)
        return ERROR_CODE

    if target == ParserArgs.UPDATE.name:
        return 0

    # check that action is defined
    action = args.pop(ParserArgs.ACTION)
    if action is None:
        FormattedParser.active_sub_parser.error(
            'action is required', need_to_exit=False)
        return ERROR_CODE

    # check that target is config and do action with it
    if target == ParserArgs.CONFIG.name:
        if action == ParserArgs.SET:
            return _set_configuration(args)

        if action == ParserArgs.RESET:
            conf_type_obj = args.pop(ParserArgs.CONFIG_TYPE.name)
            return _reset_configuration(conf_type_obj)

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
            long = args.pop(ParserArgs.LONG.dest)
            sortby = args.pop(ParserArgs.SORT_BY.dest)
            return _show_user_tasks(library, long, sortby)

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
                library=library,
                sortby=args.pop(ParserArgs.SORT_BY.dest)
            )

        if action == ParserArgs.FIND:
            name = args.pop(ParserArgs.QUEUE_NAME.name)
            return _find_queues(name, library)

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
            return _find_task(args, library)

        if action == ParserArgs.ACTIVATE:
            key = args.pop(ParserArgs.KEY.name)
            return _activate_task(key, library)

    # check that target is plan and do action with it
    if target == ParserArgs.PLAN.name:
        if action == ParserArgs.ADD:
            name = args.pop(ParserArgs.PLAN_NAME.name)
            period = args.pop(ParserArgs.PLAN_PERIOD.name)
            activation_time = args.pop(ParserArgs.PLAN_ACTIVATION_TIME.name)
            reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
            return _add_plan(name, activation_time, period, reminder, library)

        if action == ParserArgs.SET:
            key = args.pop(ParserArgs.KEY.name)
            new_name = args.pop(ParserArgs.PLAN_NAME_OPTIONAL.dest)
            period = args.pop(ParserArgs.PLAN_PERIOD_OPTIONAL.dest)
            activation_time = args.pop(
                ParserArgs.PLAN_ACTIVATION_TIME_OPTIONAL.dest)

            reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
            return _edit_plan(key, new_name, period, activation_time,
                              reminder, library)

        if action == ParserArgs.SHOW:
            return _show_plans(library)

        if action == ParserArgs.DELETE:
            key = args.pop(ParserArgs.KEY.name)
            return _delete_plan(key, library)

    if target == ParserArgs.NOTIFICATIONS.name:
        if action == ParserArgs.SHOW:
            notifications = library.online_user.notifications
            print('Notifications for user "{}":'.format(
                library.online_user.nick)
            )
            if _show_messages(notifications):
                print('Notifications not found!')
            library.clear_new_messages()

        if action == ParserArgs.DELETE:
            _del_notifications(
                library,
                _all=args.pop(ParserArgs.ALL.dest),
                old=args.pop(ParserArgs.OLD.dest)
            )


# =================================================
# functions for work with user's account instance =
# =================================================
@log_cli
def _set_configuration(args):
    """
    This method using for set configurations of program and logger
    :param args: arguments from user console input
    :return: exit code
    """
    conf_type_obj = args.pop(ParserArgs.CONFIG_TYPE.name)
    if conf_type_obj == ParserArgs.SETTINGS.name:
        storage_path = args.pop(ParserArgs.STORAGE_PATH.dest)
        try:
            Configuration.edit_settings(storage_path)
        except Exception as e:
            sys.stderr.write(str(e))
            return ERROR_CODE
        print('Program settings edited...')

    elif conf_type_obj == ParserArgs.LOGGER.name:
        level = args.pop(ParserArgs.LOGGER_LEVEL.dest)
        enabled = args.pop(ParserArgs.ENABLED_LOGGER.dest)
        log_file_path = args.pop(ParserArgs.LOG_FILE_PATH.dest)

        Configuration.edit_logger_configs(Files.LOG_CONFIG, level, enabled,
                                          log_file_path)
        print('Logger configs edited...')
    return 0


@log_cli
def _reset_configuration(conf_type_obj):
    if (conf_type_obj == ParserArgs.LOGGER.name and
            os.path.exists(Files.LOG_CONFIG)):

        os.remove(Files.LOG_CONFIG)
        print('Logger configs reset...')

    if (conf_type_obj == ParserArgs.SETTINGS.name and
            os.path.exists(Files.SETTINGS)):
        Files.set_default()
        Configuration.reset_settings()
        os.remove(Files.SETTINGS)
        print('Program settings reset...')
    return 0


# =================================================
# functions for work with user's account instance =
# =================================================
@log_cli
def _add_user(nick, password, users_storage, library: Interface):
    """
    Function for creating user. Use call from library interface for creating u
    user in library
    :param nick: user nick
    :param password: user password
    :param users_storage: place where store all users
    :param library: library interface, join all library functions in one
    interface
    :return: int - error code
    """
    try:
        users_storage.add_user(nick, password)
    except SaveUserError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    uid = uuid.uuid4().int
    queue_key = os.urandom(QUEUE_KEY_BYTES).hex()
    library.add_user(nick, uid, queue_key)
    print('User "{}" successfully created!'.format(nick))
    return 0


@log_cli
def _login(nick, password, users_storage, library) -> int:
    """
    Function for login user in system
    :param nick: user nick
    :param password: user password
    :param users_storage: place where store all users
    :param library: library interface, join all library functions in one
    interface
    :return: error code or 0 in case success
    """
    controller = UserWrapperController(users_storage)
    try:
        controller.login(nick, password)
    except LoginError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('User "{}" now is online.'.format(nick))
    library.set_online_user(nick)
    _show_new_messages(library)
    return 0


@log_cli
def _logout(users_storage) -> int:
    """
    :param users_storage:
    :return: error code or 0 in case success
    """
    controller = UserWrapperController(users_storage)
    try:
        controller.logout()
    except LogoutError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('All users now offline.')
    return 0


@log_cli
def _show_new_messages(library) -> int:
    if library.online_user is None:
        return ERROR_CODE
    new_messages = library.online_user.new_messages
    if new_messages:
        print('Reminders and new messages:')
        _show_messages(new_messages)
        library.clear_new_messages()
        print(Printer.LINE)
    return 0


@log_cli
def _show_messages(messages) -> int:
    if messages:
        reminders = []
        for message in messages[:]:  # type: str
            if message.lower().startswith('reminder'):
                reminders.append(message)
                messages.remove(message)
        Printer.print_reminders(reversed(reminders))
        print()
        Printer.print_notifications(reversed(messages))
        return 0

    return ERROR_CODE


@log_cli
def _del_notifications(library, _all, old) -> int:
    try:
        library.clear_notifications(old)

    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Notifications deleted')
    return 0


@log_cli
def _show_user_tasks(library, long, sortby) -> int:
    try:
        print('User: "{}".'.format(library.get_online_user().nick))
        queues = library.get_user_queues()
        Printer.print_queues(queues)

    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    if sortby is None:
        sortby = ParserArgs.TASK_PRIORITY.dest.lower()

    author_tasks, responsible_tasks = library.get_user_tasks()
    print('Tasks:')
    author_tasks.sort(key=lambda x: x.__dict__[sortby], reverse=True)
    responsible_tasks.sort(key=lambda x: x.__dict__[sortby], reverse=True)
    Printer.print_tasks(author_tasks, "Author", long)
    Printer.print_tasks(responsible_tasks, "Responsible", long)
    return 0


# =================================================
# functions for work with queue instance          =
# =================================================
@log_cli
def _add_queue(name, library):
    key = os.urandom(QUEUE_KEY_BYTES).hex()
    try:
        added_queue = library.add_queue(name=name, key=key)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Queue "{}" added. It\'s key - {}'.format(added_queue.name, key))
    return 0


@log_cli
def _del_queue(key, recursive, library):
    try:
        deleted_queue = library.remove_queue(
            key=key,
            recursive=recursive)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Queue "{}" deleted'.format(deleted_queue.name))
    return 0


@log_cli
def _edit_queue(key, new_name, library):
    try:
        new_name = check_str_len(new_name)
    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    try:
        library.edit_queue(key, new_name)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Queue {} now have new name "{}"'.format(key, new_name))
    return 0


@log_cli
def _show_queue(library) -> int:
    try:
        queues = library.get_user_queues()
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    for queue in queues:
        print('Queue name: "{}", key = {}'.format(queue.name, queue.key))
    return 0


@log_cli
def _show_queue_tasks(key, library, opened, archive, failed, long, sortby):
    def load_tasks(task_keys):
        _tasks = []
        for _key in task_keys:
            task = library.get_task(key=_key)
            _tasks.append(task)
        _tasks.sort(key=lambda x: x.__dict__[sortby], reverse=True)
        return _tasks

    if not opened and not archive and not failed:
        opened = True
    try:
        queue = library.get_queue(key)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    if sortby is None:
        sortby = ParserArgs.TASK_PRIORITY.dest.lower()

    print('Queue: "{}", key {}\nTasks:'.format(queue.name, queue.key))

    if opened:
        tasks = load_tasks(queue.opened_tasks)
        Printer.print_tasks(tasks, TaskStatus.OPENED, long, Printer.CL_YELLOW)

    if archive:
        tasks = load_tasks(queue.solved_tasks)
        Printer.print_tasks(tasks, TaskStatus.SOLVED, long, Printer.CL_BLUE)

    if failed:
        tasks = load_tasks(queue.failed_tasks)
        Printer.print_tasks(tasks, TaskStatus.FAILED, long, Printer.CL_RED)

    return 0


@log_cli
def _find_queues(name, library: Interface) -> int:
    queues = library.find_queues(name)
    print('Search:')
    Printer.print_queues(queues, 'Results for "{}"'.format(name))
    return 0


# =================================================
# functions for work with task instance           =
# =================================================
@log_cli
def _add_task(args, library) -> int:
    key = os.urandom(TASK_KEY_BYTES).hex()
    queue_key = args.pop(ParserArgs.TASK_QUEUE.dest)

    try:

        name = args.pop(ParserArgs.TASK_NAME.name).strip(' ')
        name = check_str_len(name)

        description = args.pop(ParserArgs.TASK_DESCRIPTION.dest)
        description = check_str_len(description)

        related = args.pop(ParserArgs.TASK_RELATED.dest)
        check_related_correctness(related)

        responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
        responsible = check_responsible_correctness(responsible)

        priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
        priority = check_priority_correctness(priority)

        progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
        progress = check_progress_correctness(progress)

        start = args.pop(ParserArgs.TASK_START.dest)
        start = check_time_format(start, entity=ParserArgs.TASK.name)

        deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
        deadline = check_time_format(deadline, entity=ParserArgs.TASK.name)

        check_terms_correctness(start, deadline)

        tags = args.pop(ParserArgs.TASK_TAGS.dest)
        tags = check_tags_correctness(tags)

        reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
        reminder = check_reminder_format(reminder, entity=ParserArgs.TASK.name)

    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    try:
        library.create_task(name, queue_key, description,
                            args.pop(ParserArgs.TASK_PARENT.dest), related,
                            responsible,
                            priority, progress, start, deadline, tags, reminder,
                            key
                            )

    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Task "{}" added. It\'s key - {}'.format(name, key))
    return 0


@log_cli
def _edit_task(args, library) -> int:
    key = args.pop(ParserArgs.KEY.name)

    try:
        name = args.pop(ParserArgs.NEW_NAME.dest)
        name = check_str_len(name)

        description = args.pop(ParserArgs.TASK_DESCRIPTION.dest)
        description = check_str_len(description)

        related = args.pop(ParserArgs.TASK_RELATED.dest)
        check_related_correctness(related, action=ParserArgs.SET)

        responsible = args.pop(ParserArgs.TASK_RESPONSIBLE.dest)
        responsible = check_responsible_correctness(responsible,
                                                    action=ParserArgs.SET)

        priority = args.pop(ParserArgs.TASK_PRIORITY.dest)
        priority = check_priority_correctness(priority, action=ParserArgs.SET)

        progress = args.pop(ParserArgs.TASK_PROGRESS.dest)
        progress = check_progress_correctness(progress, action=ParserArgs.SET)

        start = args.pop(ParserArgs.TASK_START.dest)
        start = check_time_format(
            start, entity=ParserArgs.TASK.name, action=ParserArgs.SET)

        deadline = args.pop(ParserArgs.TASK_DEADLINE.dest)
        deadline = check_time_format(
            deadline, entity=ParserArgs.TASK.name, action=ParserArgs.SET)

        check_terms_correctness(start, deadline)

        tags = args.pop(ParserArgs.TASK_TAGS.dest)
        tags = check_tags_correctness(tags, action=ParserArgs.SET)

        reminder = args.pop(ParserArgs.TASK_REMINDER.dest)
        reminder = check_reminder_format(reminder, entity=ParserArgs.TASK.name,
                                         action=ParserArgs.SET)

        status = args.pop(ParserArgs.TASK_STATUS.dest)
        status = check_status_correctness(status, action=ParserArgs.SET)

    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    try:
        library.edit_task(key, name, description,
                          args.pop(ParserArgs.TASK_PARENT.dest), related,
                          responsible, priority, progress, start, deadline,
                          tags, reminder, status)

    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Task with key "{}" edited'.format(key))
    return 0


@log_cli
def _del_task(args, library) -> int:
    try:
        tasks = library.remove_task(
            key=args.pop(ParserArgs.KEY.name),
            recursive=args.pop(ParserArgs.RECURSIVE.dest)
        )

    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    for task in tasks:
        print('Task "{}" deleted'.format(task.name))
    return 0


@log_cli
def _show_task(key, library, long) -> int:
    try:
        task = library.get_task(key)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Main task:')
    if long:
        Printer.print_task_fully(task)
    else:
        Printer.print_task_briefly(task)

    sub_tasks = library.task_controller.get_sub_tasks(task)
    if sub_tasks:
        Printer.print_tasks(sub_tasks, "Sub tasks:")
    return 0


@log_cli
def _find_task(task_params, library) -> int:
    try:
        tasks = library.find_task(task_params)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Search:')
    Printer.print_tasks(tasks, 'Result:')
    return 0


@log_cli
def _activate_task(key, library) -> int:
    try:
        task = library.activate_task(key)
    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Participation in task "{}" is confirmed!'.format(task.name))
    return 0


# =================================================
# functions for work with plan instance           =
# =================================================
@log_cli
def _add_plan(name, activation_time, period, reminder, library) -> int:
    key = os.urandom(PLAN_KEY_BYTES).hex()
    try:
        check_period_format(period)
        check_str_len(name)
        activation_time = check_time_format(activation_time,
                                            entity=ParserArgs.PLAN.name)
        validate_activation_time(activation_time)
        reminder = check_reminder_format(reminder, entity=ParserArgs.PLAN.name)
        plan = library.add_plan(key, name, period, activation_time, reminder)
    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Plan "{}" successfully created. '
          'It\'s key - {}'.format(plan.name, plan.key)
          )

    return 0


@log_cli
def _edit_plan(key, new_name, period, activation_time, reminder,
               library) -> int:
    try:
        reminder = check_reminder_format(reminder, ParserArgs.PLAN.name,
                                         ParserArgs.SET)
        print(key)
        print(new_name)
        print(reminder)
        print(activation_time)
        plan = library.edit_plan(key, new_name, period,
                                 activation_time, reminder)

    except ValueError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Plan "{}"({}) was successfully edited.'.format(plan.name, plan.key))
    return 0


@log_cli
def _show_plans(library) -> int:
    plans = library.get_plans()
    if plans:
        print('Plans:')
        for i in range(len(plans)):
            print('{}) {}'.format(i + 1, str(plans[i])))
    else:
        print('calistra: Plans not found')

    return 0


@log_cli
def _delete_plan(key, library) -> int:
    try:
        plan = library.del_plan(key)

    except AppError as e:
        sys.stderr.write(str(e))
        return ERROR_CODE

    print('Plan "{}"({}) successfully deleted'.format(plan.name, plan.key))
    return 0
