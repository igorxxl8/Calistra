try:
    from lib.calistra_lib.storage.database import Database
except ImportError:
    from calistra_lib.storage.database import Database

# TODO: обобщить метод загрузки данных


class TaskStorage:
    def __init__(self, tasks_db: Database):
        self.tasks_db = tasks_db
        self.tasks = self.tasks_db.load()

    def add_task(self, task):
        self.tasks.append(task)
        self.record_tasks()

    def record_tasks(self):
        self.tasks_db.unload(self.tasks)
