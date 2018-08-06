import os
from .task import Task
try:
    from lib.calistra_lib.storage import json_serializer as js
except ImportError:
    from calistra_lib.storage import json_serializer as js

TASKS_FILE = os.path.join(os.environ['HOME'], 'calistra_data', 'tasks.json')


class TaskStorage:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        self.tasks = js.load([Task] * 100, TASKS_FILE)

    def add_task(self, task):
        self.tasks.append(task)

    def record_tasks(self):
        js.unload(self.tasks, TASKS_FILE)
