from .task import Task

try:
    from lib.calistra_lib.storage import json_serializer as js
except ImportError:
    from calistra_lib.storage import json_serializer as js

# TODO: обобщить метод загрузки данных


class TaskStorage:
    def __init__(self, tasks_db):
        self.tasks_db = tasks_db
        self.tasks = self.load_tasks()

    def load_tasks(self):
        return js.load([Task] * 100, self.tasks_db)

    def add_task(self, task):
        self.tasks.append(task)

    def record_tasks(self):
        js.unload(self.tasks, self.tasks_db)
