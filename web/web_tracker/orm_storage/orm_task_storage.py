from calistra_lib.task.task_storage_interface import ITaskStorage
from web_tracker.models import Task


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
        keys = eval(self.tasks.filter(key=task.key).sub_tasks())
        tasks = []
        for key in keys:
            tasks.append(self.tasks.get(key=key))
        return tasks

    def get_task_by_key(self, key):
        try:
            return self.tasks.get(key=key)
        except Exception:
            return None

    def get_task_by_name(self, name):
        return self.tasks.filter(name=name)

    def get_task_by_tag(self, tag):
        return self.tasks.filter(tags=tag)

    def save_tasks(self):
        for task in self.tasks:
            task.save()
