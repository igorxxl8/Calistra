try:
    from lib.calistra_lib.task.task_storage import TaskStorage
    from lib.calistra_lib.user.user_storage import UserStorage
except ImportError:
    from calistra_lib.task.task_storage import TaskStorage
    from calistra_lib.user.user_storage import UserStorage


# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логирование


#                        Add    Set     Show
# TODO: 1) Name            +     +
# TODO: 2) Descrip         +
# TODO: 3) Author          +     -
# TODO: 4) Priority        +     +
# TODO: 5) Progress        +
# TODO: 6) Start
# TODO: 7) Deadline
# TODO: 8) Tags            +     +
# TODO: 9) Status
# TODO: 10) Reminder
# TODO: 11) Responsible
# TODO: 12) Parent
# TODO: 13) linked


# TODO: написать перемещение задач в архив при выполнении
# TODO: перемещениче задач в проваленные при прошедшем дедлайне


class Interface:
    def __init__(self, online_user, user_db, task_db):
        self.online_user = online_user
        self.users_storage = UserStorage(user_db)
        self.tasks_storage = TaskStorage(task_db)

    def add_user(self, nick):
        self.users_storage.add_user(nick)
        self.add_queue('inbox', nick)

    def add_queue(self, name, owner=None):
        if not owner:
            fullname = ''.join([str(self.online_user), "_", name])
        else:
            fullname = ''.join([str(owner), "_", name])
        added_queue = self.tasks_storage.add_queue(fullname)
        if added_queue == 1:
            raise QueueError('Queue "{}" already exists'.format(name))
        return added_queue

    def edit_queue(self, name, new_name):
        fullname = ''.join([str(self.online_user), "_", name])
        new_fullname = ''.join([str(self.online_user), "_", new_name])
        queue = self.tasks_storage.get_queue_by_name(fullname)
        if not queue:
            raise QueueError('Unable to set new name: '
                             'Queue "{}" didn\'t found'.format(name))
        queue.name = new_fullname
        self.tasks_storage.record_tasks()
        return queue

    def del_queue(self, name, recursive):
        if name == "inbox":
            raise QueueError('Unable to delete inbox queue!')
        fullname = ''.join([str(self.online_user), "_", name])
        deleted_queue = self.tasks_storage.del_queue(fullname, recursive)
        if deleted_queue == 2:
            raise QueueError('Queue "{}" isn\'t empty. '
                             'Delete all queue tasks or '
                             'delete queue recursively'.format(name))
        if deleted_queue == 1:
            raise QueueError('Queue "{}" didn\'t found.'.format(name))
        return deleted_queue

    def get_user_queues(self):
        queues = []
        for queue in self.tasks_storage.tasks_queues:
            if self.online_user == queue.name.split('_')[0]:
                queues.append(queue)
        return queues

    def get_queue_tasks(self, queue_name):
        queue_fullname = ''.join([str(self.online_user), "_", queue_name])
        queue = self.tasks_storage.get_queue_by_name(queue_fullname)
        if queue is None:
            raise QueueError('Queue "{}" didn\'t found.'.format(queue_name))
        return queue.tasks

    def add_task(self, name, queue_name, description, parent, linked,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):

        queue_fullname = ''.join([self.online_user, "_", queue_name])
        added_task = self.tasks_storage.add_task(
            author=self.online_user, name=name, queue_name=queue_fullname,
            description=description, parent=parent, linked=linked,
            responsible=responsible, priority=priority, progress=progress,
            start=start, deadline=deadline, tags=tags,
            reminder=reminder, key=key)

        if added_task == 1:
            raise TaskError('Queue "{}" did not found'.format(queue_name))
        # TODO: добавить оповещение ответственных
        return added_task

    def edit_task(self, key, name, description, parent, linked,
                  responsible, priority, progress, start, deadline, tags,
                  reminder, status):

        task = self.tasks_storage.get_task_by_key(key)
        if task is None:
            raise TaskError('Task with key "{}" didn\'t found'.format(key))

        online_user = self.online_user
        # TODO: разрешить редактировать только автору
        if (online_user not in task.responsible and
                online_user != task.author):

            raise TaskError('Access denied: '
                            'You can not '
                            'edit this task'.format(online_user))

        if (online_user in task.responsible and
                online_user != task.author and
                (name or description or parent or linked or responsible or
                 priority or start or deadline or tags or reminder)):

            raise TaskError('You can not edit task param '
                            'besides status and progress')

        if progress:
            task.progress = progress
        if status:
            task.status = status
        if name:
            task.name = name
        if description:
            task.description = description
        if parent:
            task.parent = parent
        if linked:
            task.linked = linked
        if responsible:
            task.responsible = responsible
        if priority:
            task.priority = priority
        if start:
            task.start = start
        if deadline:
            task.deadline = deadline
        if tags:
            if tags == '?':
                task.tags = None
            else:
                task.tags = tags
        if reminder:
            task.reminder = reminder
        self.tasks_storage.record_tasks()
        # TODO: оповещение ответственных

    def del_task(self, key, recursive):
        task = self.tasks_storage.get_task_by_key(key)
        if task is None:
            raise TaskError('Task with key "{}" didn\'t found'.format(key))
        deleted_taks = self.tasks_storage.del_task(task, recursive)
        if deleted_taks is None:
            raise TaskError('Can not delete task. It has subtasks. '
                            'Delete all subtasks or delete task recursively')
        self.tasks_storage.record_tasks()
        # TODO: добавить уведомлении о удалении задачи ответственным

    def add_plan(self):
        pass

    def del_plan(self):
        pass

    def edit_plan(self):
        pass


class QueueError(Exception):
    def __init__(self, message):
        self.message = message


class TaskError(Exception):
    def __init__(self, message):
        self.message = message
