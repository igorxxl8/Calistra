from .task import Task

from calistra_lib.queue.queue import Queue
from calistra_lib.storage.database import Database


# TODO: обобщить метод загрузки данных
# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование

class TaskStorage:
    def __init__(self, tasks_db: Database):
        self.tasks_db = tasks_db
        self.tasks = self.tasks_db.load()

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def get_sub_tasks(self, task: Task):
        sub_tasks = []
        for sub_task_key in task.sub_tasks:
            sub_task = self.get_task_by_key(sub_task_key)
            sub_tasks.append(sub_task)
        return sub_tasks

    def get_task_by_key(self, key):
        for task in self.tasks:
            if task.key == key:
                return task

    def get_task_by_name(self, name):
        tasks = []
        for task in self.tasks:
            if task.name == name or task.name.startswith(name):
                tasks.append(task)
        return tasks

    def save_tasks(self):
        self.tasks_db.unload(self.tasks)
