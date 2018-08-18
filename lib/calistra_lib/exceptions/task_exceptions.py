from .base_exception import AppError


class TaskNotFoundError(AppError):
    def __init__(self, message):
        message = ''.join(['Task not found: ', message])
        super().__init__(message)


class SubTaskError(AppError):
    def __init__(self, message):
        message = ''.join(['Sub task error: ', message])
        super().__init__(message)


class AddingTaskError(AppError):
    def __init__(self, message):
        message = ''.join(['Adding task error: ', message])
        super().__init__(message)


class DeletingTaskError(AppError):
    def __init__(self, message):
        message = ''.join(['Deleting task error: ', message])
        super().__init__(message)


class TaskStatusError(AppError):
    def __init__(self, message):
        message = ''.join(['Task status error: ', message])
        super().__init__(message)


class TaskDeadlineError(AppError):
    def __init__(self, message):
        message = ''.join(['Deadline error: ', message])
        super().__init__(message)
