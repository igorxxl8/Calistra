from .base_exception import AppError


class QueueNotFoundError(AppError):
    def __init__(self, message):
        message = ''.join(['Queue not found: ', message])
        super().__init__(message)


class AddingQueueError(AppError):
    def __init__(self, message):
        message = ''.join(['Adding queue error: ', message])
        super().__init__(message)


class DeletingQueueError(AppError):
    def __init__(self, message):
        message = ''.join(['Deleting queue error: ', message])
        super().__init__(message)


class EditingQueueError(AppError):
    def __init__(self, message):
        message = ''.join(['Editing queue error: ', message])
        super().__init__(message)
