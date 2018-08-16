# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование


class Queue:
    def __init__(self, name, key, owner, tasks, archive):
        self.name = name
        self.key = key
        self.owner = owner
        self.tasks = tasks
        self.archive = archive
