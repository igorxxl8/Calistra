class Messages:
    SIGN_IN = 'please sign in system'
    TASK_WAS_DELETED = 'The task {} was deleted'
    TASK_WAS_FAILED = 'The task {} was failed'
    SHOW_KEY = 'key - {}'
    SHOW_PARENT_KEY = 'parent task key "{}"'
    CANNOT_SEE_TASK = 'you cannot see this task'
    CANNOT_SEE_QUEUE = 'you cannot see this queue'
    CANNOT_EDIT_QUEUE = 'you cannot edit this queue'
    CANNOT_DELETE_QUEUE = 'you cannot delete this queue'
    CANNOT_EDIT_TASK = 'you cannot edit this task'
    CANNOT_DELETE_TASK = 'you cannot delete this task.'
    CANNOT_SET_STATUS_FAILED = 'cannot set status "failed". Task already failed'
    CANNOT_EDIT_PARAM = 'You cannot edit task param besides status and progress'
    NEED_ACTIVATE_TASK = 'you need to activate this task'
    YOU_ASSIGNED = ('User "{}" assigned you responsible for the task:'
                    ' "{}", key - {}. You need to confirm participation')
    YOU_SUSPENDED = 'You are suspended from task execution: "{}".'
    ALREADY_CONFIRMED = 'you already confirmed'
    CANNOT_ACTIVATE = 'you cannot activate this task. You not responsible'
    USER_CONFIRMED = ('User "{}" confirmed participation in the task "{}", '
                      'key - {}')

    USER_NOT_FOUND = 'User not found: name - "{}"'
    DEFAULT_QUEUE_IMMUTABLE = 'default queue "{}" immutable'
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
