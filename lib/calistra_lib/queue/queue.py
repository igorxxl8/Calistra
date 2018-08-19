# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логгирование


class Queue:
    def __init__(self, name, key, owner, opened_tasks=None, solved_tasks=None):
        self.name = name
        self.key = key
        self.owner = owner
        self.failed_tasks = []
        if opened_tasks is None:
            self.opened_tasks = []
        if solved_tasks is None:
            self.solved_tasks = []
