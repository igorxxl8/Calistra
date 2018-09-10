from calistra_lib.task.task_storage_interface import ITaskStorage
from ..models import Task


class ORMTaskStorage(ITaskStorage):
    def __init__(self):
        super().__init__(Task.objects.all())

    def add_task(self, task):
        self.tasks.create(
            name=task.name,
            description=str(task.description),
            queue=str(task.queue),
            parent=str(task.parent),
            sub_tasks=str(task.sub_tasks),
            related=str(task.related),
            author=str(task.author),
            priority=task.priority,
            progress=task.progress,
            start=str(task.start),
            deadline=str(task.deadline),
            tags=str(task.tags),
            reminder=str(task.reminder),
            status=task.status,
            key=task.key,
            creating_time=task.creating_time,
            editing_time=task.editing_time,
            responsible=str(task.responsible)
        )

    def remove_task(self, task):
        self.tasks.get(key=task.key).delete()

    def get_sub_tasks(self, task):
        keys = task.sub_tasks.split(',')
        tasks = []
        for key in keys:
            task = self.get_task_by_key(key)
            if task:
                tasks.append(task)
        return tasks

    def get_task_by_key(self, key):
        try:
            return self.tasks.get(key=key)
        except Exception:
            return None

    def get_task_by_name(self, name):
        return self.tasks.filter(name=name)

    def get_tasks_by_author(self, author):
        return self.tasks.filter(author=author.nick)

    def get_tasks_by_responsible(self, responsible):
        tasks = []
        for task in self.tasks:
            temp = task.responsible.split(',')
            if responsible.nick in temp:
                tasks.append(task)

        return tasks

    def get_task_by_tag(self, tag):
        return self.tasks.filter(tags=tag)

    def save_tasks(self):
        for task in self.tasks:
            task.save()

    def get_opened_tasks(self, queue):
        temp = queue.opened_tasks.split(',')
        tasks = []
        for key in temp:
            task = self.get_task_by_key(key)
            if task is not None:
                tasks.append(task)
        return tasks

    def get_solved_tasks(self, queue):
        temp = queue.solved_tasks.split(',')
        tasks = []
        for key in temp:
            task = self.get_task_by_key(key)
            if task is not None:
                tasks.append(task)
        return tasks

    def get_failed_tasks(self, queue):
        temp = queue.failed_tasks.split(',')
        tasks = []
        for key in temp:
            task = self.get_task_by_key(key)
            if task is not None:
                tasks.append(task)
        return tasks

    def delete_queue_tasks(self, queue):
        tasks = (self.get_opened_tasks(queue) +
                 self.get_solved_tasks(queue) +
                 self.get_failed_tasks(queue))
        for task in tasks:
            self.remove_task(task)
