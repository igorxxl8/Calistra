"""
This module contains ParserArgs class which store constants
using by argumnt parser
"""

from collections import namedtuple


class ParserArgs:
    """Constants, which using in parser as commands and
    settings for arguments
    """

    # tuple for represent positional argument parser
    Argument = namedtuple('Argument', ['name', 'help'])

    # tuple for desctibe optional argument for parser
    OptionalArgument = namedtuple('OptionalArgument',
                                  ['dest', 'long', 'short', 'help']
                                  )
    __STORE_TRUE__ = "store_true"

    # main parser's arguments which using in different types of parsers
    DESCRIPTION = 'Calistra - task tracker'
    TARGET = Argument(name='target', help='select a target to work with')
    ACTION = 'action'
    ADD = 'add'
    SET = 'set'
    SHOW = 'show'
    DELETE = 'del'
    FIND = 'find'
    ACTIVATE = 'activate'
    KEY = Argument(name='key', help='access key')
    UPDATE = Argument(name='update', help='update all entities')
    RECURSIVE = OptionalArgument(
        dest='recursive',
        long='--recursive',
        short='-r',
        help='applying an action to nested objects'
    )

    ALL = OptionalArgument(
        dest='all',
        long='--all',
        short='-a',
        help='apply operation for all objects'
    )

    OLD = OptionalArgument(
        dest='quantity',
        long='--old',
        short='-o',
        help='apply operation for define number of old objects.'
    )

    LONG = OptionalArgument(
        dest='LONG',
        long='--long',
        short='-l',
        help='show full info'
    )

    SORT_BY = OptionalArgument(
        dest='SORTBY',
        long='--sortby',
        short='-sb',
        help='task field for sort'
    )
    SORT_BY_CHOICES = ['deadline', 'priority', 'progress', 'editing_time',
                       'name']

    # Constants, which represent user parser commands and settings
    USER = Argument(name='user', help='work with user\'s account')
    USER_ACTION = 'action with user'
    LOGIN = Argument(name='login', help='login with nickname and password')
    LOGOUT = Argument(name='logout', help='log out of user\'s session')
    NICKNAME = Argument(name='nick', help='user\'s nickname')
    PASSWORD = Argument(name='pasw', help='user\'s password')
    ADD_USER_HELP = 'add new user'
    SET_USER_HELP = 'edit current user'
    SHOW_USER_HELP = 'show user queues and tasks'
    NOTIFICATIONS = Argument(name='ntf', help='user notifications')
    NTF_ACTION = 'action with notifications'
    SHOW_NTF_HELP = 'show all user notifications'
    DELETE_NTF = 'delete notifications'

    # Constants, which represent task parser commands and settings
    TASK = Argument(name='task', help='work with single task')
    TASK_ACTION = 'action with task'
    ADD_TASK_HELP = 'add new task'
    DELETE_TASK_HELP = 'delete existing task'
    FIND_TASK_HELP = 'find task'
    SET_TASK_HELP = 'edit task'
    SHOW_TASK_HELP = 'show user\'s tasks'
    ACTIVATE_TASK_HELP = 'confirm participation (for responsible user only)'
    TASK_NAME = Argument(name='name', help='name for task')

    # optional task params
    NEW_NAME = OptionalArgument(
        dest='NEW_NAME',
        long='--new_name',
        short='-nn',
        help='define new name for tasks, queues and other'
    )

    TASK_QUEUE = OptionalArgument(
        dest='QK',
        long='--queue',
        short='-q',
        help='queue key where the tasks placed')

    TASK_DESCRIPTION = OptionalArgument(
        dest='DESCR',
        long='--description',
        short='-d',
        help='info about task'
    )

    TASK_PARENT = OptionalArgument(
        dest='PARENT',
        long='--parent',
        short='-pr',
        help='the key of the parent task. The parent task must be '
             'in the same queue as the edited task. Type "?" to reset'
    )

    TASK_RELATED = OptionalArgument(
        dest='RELATED',
        long='--related',
        short='-li',
        help='key and type of related task. '
             'Format: "related_tasks_keys:related_task_type" '
             '(blocker or controller):'
             'blocker - this task cannot be solved, while not solved blocker '
             'tasks, controller - the task-controller sets the same status'
             ' to the current task (there can be only one controller task).'
             'In format avoid spaces. '
             'For example: "89fdsg8s9df,9f08g98990:blocker"'
    )

    TASK_PRIORITY = OptionalArgument(
        dest='PRIORITY',
        long='--priority',
        short='-p',
        help='task priority: high (10), medium (0), low (-10)'
             ' or user numbers in range -10..10'
    )

    TASK_PROGRESS = OptionalArgument(
        dest='PROGRESS',
        long='--progress',
        short='-pr',
        help='task progress in range (0-100) percent. Type "?" to reset'
    )

    TASK_START = OptionalArgument(
        dest='START',
        long='--starts',
        short='-s',
        help='time, when task begin. It must have correct number of days '
             'in month, month in year, hour and minutes. '
             'Format: "day.month.year.hour:min" (only numbers allowed, '
             'ex. "12.08.2028.9:00". '
             'or type symbol "?" to erase start time for task)'
    )

    TASK_DEADLINE = OptionalArgument(
        dest='DEADLINE',
        long='--deadline',
        short='-dl',
        help='the deadline for the completion of a task.'
             'Format: "day.month.year.hour:min" (only numbers allowed)'
             'or type symbol "?" to erase deadline for task'
    )

    TASK_TAGS = OptionalArgument(
        dest='TAGS',
        long='--tags',
        short='-t',
        help='marks for task, defines category or group. '
             'Format: "tag1,tag2,tag3" (avoid space near comma)'
             ' or type symbol "?" to erase all tags'
    )

    TASK_REMINDER = OptionalArgument(
        dest='REMINDER',
        long='--reminder',
        short='-re',
        help='time, when app warns user about necessary to perform a task. '
             'Format: "frequency:time", '
             'frequency - every_week, every_day, or day of week(monday, '
             'tuesday, wednesday, thursday, friday, saturday, sunday)'
             'for example: "every_day:17.00" or "monday,tuesday:17.00,18.00". '
             'You cannot mix day of week with every_day or every_week!'
    )

    TASK_RESPONSIBLE = OptionalArgument(
        dest='RESP',
        long='--responsible',
        short='-rp',
        help='users how can access this task and can perform it.'
             'Format: "user1,user2,user3" (avoid space near comma)'
    )

    TASK_STATUS = OptionalArgument(
        dest='STATUS',
        long='--status',
        short='-st',
        help='define task status: opened, solved or activated'
    )

    # Constants for work with queues
    QUEUE = Argument(name='queue', help='work with group of task')
    QUEUE_ACTION = 'action with queue'
    ADD_QUEUE_HELP = 'add new queue'
    FIND_QUEUE_HELP = 'find queue by name'
    SET_QUEUE_HELP = 'edit queue'
    DELETE_QUEUE_HELP = 'delete existing queue'
    SHOW_QUEUE_HELP = ('show user tasks in queue with defined key'
                       '(opened tasks by default)')
    QUEUE_NAME = Argument(name='name', help='queue name')

    # optional queues arguments
    OPEN_TASKS = OptionalArgument(
        long='--opened',
        short='-op',
        dest='OPEN',
        help='perform for opened tasks'
    )

    SOLVED_TASKS = OptionalArgument(
        long='--solved',
        short='-do',
        dest='SOLVED',
        help='perform for solved tasks'
    )

    FAILED_TASKS = OptionalArgument(
        long='--failed',
        short='-f',
        dest='FAILED',
        help='perform for failed tasks'
    )

    # Constants, which represent plan parser commands and settings
    PLAN = Argument(name='plan', help='work with plans')
    PLAN_ACTION = 'action with plans'
    ADD_PLAN = 'add new periodic plan'
    SET_PLAN = 'edit existing plan'
    DEL_PLAN = 'remove plan'
    SHOW_PLAN_HELP = 'show all plans'

    PLAN_NAME = Argument(name='name', help='the name of the plan that creates'
                                           ' the task with the same name')

    PLAN_PERIOD = Argument(name='period', help='plan time interval. Choose '
                                               'from: daily, weekly, monthly,'
                                               ' yearly')

    PLAN_ACTIVATION_TIME = Argument(
        name='time',
        help='time when plan create task.Format: day.month.year.hour:minutes. '
             'For example: 20.08.2018.9:00'
    )

    # optional args for plan
    PLAN_NAME_OPTIONAL = OptionalArgument(
        long='--new_name',
        short='-pn',
        dest='NEW_NAME',
        help='new name for plan'
    )

    PLAN_PERIOD_OPTIONAL = OptionalArgument(
        long='--period',
        short='-pe',
        dest='PERIOD',
        help='new period for plan'
    )

    PLAN_ACTIVATION_TIME_OPTIONAL = OptionalArgument(
        long='--activation',
        short='-ac',
        dest='ACTIVATION',
        help='new time when plan will be activated and create task'
    )
