from .task import Task
from .queue import Queue
from .task_exceptions import QueueError, TaskError

try:
    from lib.calistra_lib.storage.database import Database
except ImportError:
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

    def add_queue(self, name, key, owner):
        self.tasks_queues.append(Queue(name, key, owner, [], []))
        return self.tasks_queues[-1]

    def remove_queue(self, queue):
        self.tasks_queues.remove(queue)

    def get_queue_by_key(self, key):
        for queue in self.tasks_queues:  # type: Queue
            if key == queue.key:
                return queue

    def get_queue_with_task(self, task):
        for queue in self.tasks_queues:
            for queue_task in queue.tasks:
                if queue_task is task:
                    return queue

    @staticmethod
    def add_task(queue, name, description, parent, linked, author,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key):

        new_task = Task(
            name=name, description=description, parent=parent, linked=linked,
            author=author, responsible=responsible, priority=priority,
            progress=progress, start=start, deadline=deadline,
            tags=tags, reminder=reminder, key=key)

        queue.tasks.append(new_task)
        return new_task

    def remove_task(self, task):
        for queue in self.tasks_queues:  # type: Queue
            for q_task in queue.tasks:  # type: Task
                if q_task.key == task.key:
                    queue.tasks.remove(q_task)

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

    def get_task_by_name(self, name):
        tasks = []
        for task in self.tasks:
            if task.name == name:
                tasks.append(task)
        return tasks

    def save_tasks(self):
        self.tasks_db.unload(self.tasks_queues)
