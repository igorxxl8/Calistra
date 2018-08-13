try:
    from lib.calistra_lib.task.task import Task
    from lib.calistra_lib.task.queue import Queue
    from lib.calistra_lib.storage.database import Database
except ImportError:
    from calistra_lib.task.task import Task
    from calistra_lib.task.queue import Queue
    from calistra_lib.storage.database import Database


# TODO: обобщить метод загрузки данных
# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование

class TaskStorage:
    def __init__(self, tasks_db: Database):
        self.tasks_db = tasks_db
        self.tasks_queues = self.tasks_db.load()  # type: list
        self.tasks = self.get_all_tasks()

    def get_all_tasks(self):
        tasks = []
        for queue in self.tasks_queues:
            tasks += queue.tasks
        return tasks

    def add_queue(self, name):
        if self.get_queue_by_name(name):
            return 1
        new_queue = Queue(name, [], [])
        self.tasks_queues.append(new_queue)
        self.record_tasks()
        return new_queue

    def get_queue_by_name(self, name):
        for queue in self.tasks_queues:  # type: Queue
            if name == queue.name:
                return queue

    def del_queue(self, name, recursive):
        queue = self.get_queue_by_name(name)
        if not queue:
            return 1
        if not recursive and queue.tasks:
            return 2
        self.tasks_queues.remove(queue)
        self.record_tasks()
        return queue

    def add_task(self, queue_name, name, description, parent, linked, author,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):

        new_task = Task(
            name=name, description=description, parent=parent, linked=linked,
            author=author, responsible=responsible, priority=priority,
            progress=progress, start=start, deadline=deadline,
            tags=tags, reminder=reminder, key=key)

        for queue in self.tasks_queues:  # type: Queue
            if queue_name == queue.name:
                queue.tasks.append(new_task)
                self.record_tasks()
                return new_task
        return 1

    def del_task(self, task, recursive):
        for queue in self.tasks_queues:  # type: Queue
            if task in queue.tasks:
                subtasks = self.get_subtasks(task)
                if not subtasks:
                    queue.tasks.remove(task)
                    return task
                if not recursive:
                    return None
                queue.tasks.remove(task)
                for subtask in subtasks:
                    self.del_task(subtask, recursive)
                return task

    def get_subtasks(self, parent_task: Task):
        subtasks = []
        for task in self.tasks:
            if task.parent == parent_task.key:
                subtasks.append(task)
        return subtasks

    def get_task_by_key(self, key):
        for task in self.tasks:
            if task.key == key:
                return task

    def record_tasks(self):
        self.tasks_db.unload(self.tasks_queues)
