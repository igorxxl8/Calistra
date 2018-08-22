class Messages:
    QUEUES_NOT_FOUND = 'Queues not found.'
    SIGN_IN = 'please sign in system'
    TASK_WAS_DELETED = 'The task "{}"({}) was deleted by author - "{}"'
    TASK_WAS_FAILED = 'The task "{}" was failed'
    TASK_WAS_FAILED_DEADLINE_PASSED = ('task "{}"({}) failed. '
                                       'The deadline has passed - {}')

    TASK_REOPENED = 'The task "{}" reopened by user "{}"'
    TASK_SOLVED = 'The task "{}" was solved by user "{}"'
    SHOW_KEY = 'key - {}'
    SHOW_PARENT_KEY = 'parent task key - {}'
    CANNOT_SEE_TASK = 'you cannot see this task'
    CANNOT_SEE_QUEUE = 'you cannot see this queue'
    CANNOT_EDIT_QUEUE = 'you cannot edit this queue'
    CANNOT_DELETE_QUEUE = 'you cannot delete this queue'
    CANNOT_EDIT_TASK = 'you cannot edit this task'
    CANNOT_DELETE_TASK = 'you cannot delete this task.'
    CANNOT_SET_STATUS_FAILED = 'cannot set status "failed". Task already failed'
    CANNOT_EDIT_PARAM = 'You cannot edit task param besides status and progress'
    CANNOT_USE_SOMEONE_ELSE_TASK = ('you cannot use someone else task. '
                                    'Use only tasks created by you and '
                                    'task, where you take participation!')

    CANNOT_USE_TASK_AS_BLOCKER = ('you cannot use task "{}"({}) as blocker,'
                                  'this task already solved.')

    TASK_WAS_UPDATED_BY_CONTROLLER = ('Task "{}" was {} by related controller'
                                      ' task.')

    TASK_CANNOT_BE_RELATED_TO_ITSELF = ('the task cannot be related to itself.'
                                        ' Task key - {}.')

    CANNOT_LINK_TASK_WITH_SOLVED_TASK = ('you cannot relate a task with'
                                         ' solved or failed task - "{}", '
                                         'key - {}.')

    CANNOT_CHANGE_RELATED_TASK_STATUS = ('you cannot change the status '
                                         'of task which has related task. '
                                         'You can reset related controller '
                                         'task and try again.')

    CAN_BE_ONLY_ONE_CONTROLLER_TASK = ('there can be only one controller task. '
                                       '{} task keys found.')

    CANNOT_SOLVE_TASK_WITH_UNSOLVED_BLOCKERS = ('you cannot solve task. Task '
                                                'has blockers that haven\'t '
                                                'been resolved yet')
    TASK_BLOCKERS_WERE_SOLVED = ('For task "{}" all blockers were solved. '
                                 'You can solve this task too!')

    CANNOT_NAME_AS_DEFAULT_QUEUE = 'this name booked by program.'
    TASK_FAILED = 'Task {}, key {} was failed.'
    NEED_ACTIVATE_TASK = 'you need to activate this task. See help'
    CANNOT_USE_SOMEONE_ELSE_QUEUE = 'you cannot use someone else queue.'
    YOU_ASSIGNED = ('User "{}" assigned you responsible for the task:'
                    ' "{}", key - {}. You need to confirm participation.')
    YOU_SUSPENDED = 'You are suspended from task execution: "{}".'
    ALREADY_CONFIRMED = 'you already confirmed'
    CANNOT_ACTIVATE = 'you cannot activate this task. You not responsible'
    USER_CONFIRMED = ('User "{}" confirmed participation in the task "{}", '
                      'key - {}.')

    USER_NOT_FOUND = 'User not found: name - "{}"'
    DEFAULT_QUEUE_IMMUTABLE = 'default queue "{}" immutable'
    DEFAULT_QUEUE_UNREMOVABLE = 'you cannot delete default queue'
    QUEUE_NOT_EMPTY = ('queue with key "{}" isn\'t empty.Delete all queue'
                       ' tasks or delete queue recursively')

    TASK_HAS_SUBTASKS = ('task has sub tasks. Delete all sub '
                         'tasks or delete task recursively')

    CANNOT_SET_STATUS_SOLVED_FOR_FAILED = ('cannot set status "solved". '
                                           'Failed task cannot be solved. '
                                           'First of all, if necessary, change'
                                           ' deadline and open task again')
    CANNOT_SET_STATUS_SOLVED_UNS_ST = ('cannot set status "solved". Task has '
                                       'unsolved sub tasks.')

    CANNOT_SET_STATUS_SOLVED_FAILED_ST = (
        'cannot set status "solved". Task has failed sub tasks!')

    CANNOT_SET_STATUS_OPENED_FAILED_ST = (
        'cannot set status "opened". Task has failed sub tasks!'
    )

    CANNOT_SET_SAME_STATUS = 'Cannot set status "{}". Task "{}" already {}'

    TASK_ALREADY_SOLVED = 'cannot set status "solved". Task already solved'

    TASK_ALREADY_OPENED = 'cannot set status "opened". Task already opened'

    CANNOT_SET_STATUS_OPENED_FOR_FAILED = ('cannot set status "opened". '
                                           'Task failed. First of all, change'
                                           ' deadline and open task again')

    CANNOT_SET_STATUS_CLOSED = ('you cannot set status "closed". '
                                'It\'s author rights.')

    CANNOT_SET_STATUS_CLOSED_FOR_UNSOLVED = ('cannot set status "closed". '
                                             'First of all task must be solved')

    DEADLINE_CANNOT_EARLIER_NOW = ('the deadline cannot be earlier than '
                                   'current time')

    DEADLINE_CANNOT_EARLIER_START = ('the deadline for a task cannot be earlier'
                                     ' than its start')

    PARENT_IN_OTHER_QUEUE = ('sub task and its parent cannot be located in '
                             'different queues')

    PARENT_SAME_TASK = 'parent and sub task cannot be the same task'

    PARENT_IS_TASK_SUBTASK = ('parent task cannot be one of sub tasks '
                              'of this task')

    USER_EDIT_TASK = 'User "{}" edit task "{}":'

    # REMINDERS MESSAGES
    TASK_START_IN_A_HOUR = 'REMINDER: Task "{}"({}) start within an hour at {}'
    TASK_START_IN_TWO_HOURS = ('REMINDER: task "{}"({}) will start in two hours'
                               ' at {}')

    TASK_START_TOMORROW = 'task "{}"({}) starts tomorrow at {}'

    TASK_DEADLINE_IN_A_HOUR = ('REMINDER: Task "{}"({}) deadline within '
                               'an hour at {}. You should solve this task'
                               ' as soon as possible!')

    TASK_DEADLINE_IN_TWO_HOURS = ('REMINDER: Task "{}"({}) deadline in two hour'
                                  ' - {}. You should hurry!')

    TASK_DEADLINE_TOMORROW = 'task "{}"({}) deadline tomorrow at {}'

    TASK_START_TODAY = 'task "{}"({}) starts today at {}'
    TASK_BEGIN = 'today at {}, task "{}"({}) task was started'

    TASK_REMINDER = 'REMINDER: You have task "{}"({}). It\'s time to do it - {}'
