"""This module contains errors which appear when user works with queue"""


from .base_exception import AppError


class QueueNotFoundError(AppError):
    """This class describe error which happend when user try to find queue
    which doesn't exists
    """
    def __init__(self, message):
        message = ''.join(['Queue not found: ', message])
        super().__init__(message)


class AddingQueueError(AppError):
    """This class describe error which happend when user try to add queue
    which which has error
    """
    def __init__(self, message):
        message = ''.join(['Adding queue error: ', message])
        super().__init__(message)


class DeletingQueueError(AppError):
    """This class describe error which happend when user try to delete queue
    """
    def __init__(self, message):
        message = ''.join(['Deleting queue error: ', message])
        super().__init__(message)


class EditingQueueError(AppError):
    """This class describe error whick happend when user try to edit queue
    """
    def __init__(self, message):
        message = ''.join(['Editing queue error: ', message])
        super().__init__(message)
