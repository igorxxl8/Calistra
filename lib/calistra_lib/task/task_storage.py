from .task import Task
from queue.queue import Queue

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
        self.opened_tasks = self.get_opened_tasks()
        self.solved_tasks = self.get_solved_tasks()
        self.failed_tasks = self.get_failed_tasks()

    def get_all_tasks(self):
        return self.opened_tasks + self.solved_tasks + self.failed_tasks

    @staticmethod
    def get_all_queue_tasks(queue):
        return queue.opened_tasks + queue.solved_tasks + queue.failed_tasks

    def get_opened_tasks(self):
        tasks = []
        for queue in self.tasks_queues:  # type: Queue
            tasks += queue.opened_tasks
        return tasks

    def get_solved_tasks(self):
        tasks = []
        for queue in self.tasks_queues:  # type: Queue
            tasks += queue.solved_tasks
        return tasks

    def get_failed_tasks(self):
        tasks = []
        for queue in self.tasks_queues:  # type: Queue
            tasks += queue.failed_tasks
        return tasks

    def add_queue(self, name, key, owner):
        self.tasks_queues.append(Queue(name, key, owner))
        return self.tasks_queues[-1]

    def remove_queue(self, queue):
        self.tasks_queues.remove(queue)

    def get_queue_by_key(self, key):
        for queue in self.tasks_queues:  # type: Queue
            if key == queue.key:
                return queue

    def get_queue_by_name(self, name):
        results = []
        for queue in self.tasks_queues:
            if name == queue.name or queue.name.startswith(name):
                results.append(queue)
        return results

    def get_queue_with_task(self, task):
        for queue in self.tasks_queues:
            for queue_task in self.get_all_queue_tasks(queue):
                if queue_task is task:
                    return queue

    @staticmethod
    def add_task(queue, name, description, parent, linked, author,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key, creating_time):

        new_task = Task(
            name=name, description=description, parent=parent, linked=linked,
            author=author, responsible=responsible, priority=priority,
            progress=progress, start=start, deadline=deadline,
            tags=tags, reminder=reminder, key=key, creating_time=creating_time)

        queue.opened_tasks.append(new_task)
        return new_task

    @staticmethod
    def remove_solved_task(task, queue):
        queue.solved.remove(task)

    def remove_opened_task(self, task):
        for queue in self.tasks_queues:  # type: Queue
            for q_task in queue.opened_tasks:  # type: Task
                if q_task.key == task.key:
                    queue.opened_tasks.remove(q_task)

    def get_sub_tasks(self, parent_task: Task):
        sub_tasks = []
        for task in self.opened_tasks:
            if task.parent == parent_task.key:
                sub_tasks.append(task)
        return sub_tasks

    def get_task_by_key(self, key):
        for task in self.get_all_tasks():
            if task.key == key:
                return task

    def get_task_by_name(self, name):
        tasks = []
        for task in self.get_all_tasks():
            if task.name == name or task.name.startswith(name):
                tasks.append(task)

        return tasks

    def save_tasks(self):
        self.tasks_db.unload(self.tasks_queues)
