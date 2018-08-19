# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование


class TaskStatus:
    OPENED = 'opened'
    SOLVED = 'solved'
    ACTIVATED = 'activated'
    CLOSED = 'closed'
    FAILED = 'failed'


class Task:
    def __init__(self, name, queue, description, parent, linked, author,
                 responsible: list, priority, progress, start, deadline,
                 tags, reminder, key, creating_time):

        self.name = name
        self.queue = queue
        self.description = description
        self.parent = parent
        self.sub_tasks = []
        self.linked = linked
        self.author = author
        self.priority = priority
        self.progress = progress
        self.start = start
        self.deadline = deadline
        self.tags = tags
        self.reminder = reminder
        self.status = TaskStatus.OPENED
        self.key = key
        self.creating_teme = creating_time
        self.editing_time = creating_time

        if responsible is None:
            self.responsible = []
        else:
            self.responsible = responsible
