from .task import Task

try:
    from lib.calistra_lib.queue.queue import Queue
    from lib.calistra_lib.storage.database import Database
except ImportError:
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

    def add_task(self, queue, name, description, parent, linked, author,
                 responsible, priority, progress, start, deadline, tags,
                 reminder, key, creating_time):

        task = Task(queue=queue.key, name=name, description=description,
                    parent=parent, linked=linked, author=author.nick,
                    responsible=responsible, priority=priority,
                    progress=progress, start=start, deadline=deadline,
                    tags=tags, reminder=reminder, key=key,
                    creating_time=creating_time)

        self.tasks.append(task)
        return task

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
