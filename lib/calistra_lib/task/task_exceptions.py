class QueueError(Exception):
    def __init__(self, message):
        self.message = message


class TaskError(Exception):
    def __init__(self, message):
        self.message = message