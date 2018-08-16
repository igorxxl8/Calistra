# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование


class Task:
    def __init__(self, name, description, parent, linked, author,
                 responsible: list, priority, progress, start, deadline,
                 tags, reminder, key):

        self.name = name
        self.description = description
        self.parent = parent
        self.linked = linked
        self.author = author
        self.priority = priority
        self.progress = progress
        self.start = start
        self.deadline = deadline
        self.tags = tags
        self.reminder = reminder
        self.status = 'opened'
        self.key = key

        if responsible is None:
            self.responsible = []
        else:
            self.responsible = responsible
