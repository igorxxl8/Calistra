"""
This module contains errors which appear when user work with task entities
"""

from .base_exception import AppError


class TaskNotFoundError(AppError):
    """This class describe error which appear when user try to find task
    which not exists"""
    def __init__(self, message):
        message = ''.join(['Task not found: ', message])
        super().__init__(message)


class RelatedTaskError(AppError):
    """
    This class describe error which appear when user try to work with
    incorrect related task
    """
    def __init__(self, message):
        message = ''.join(['Task cannot be related: ', message])
        super().__init__(message)


class SubTaskError(AppError):
    """
    This class describe error which appear when user try to work with
    incorrect sub task
    """
    def __init__(self, message):
        message = ''.join(['Sub task error: ', message])
        super().__init__(message)


class AddingTaskError(AppError):
    """
    This class describe error which appear when user try to add task
    """
    def __init__(self, message):
        message = ''.join(['Adding task error: ', message])
        super().__init__(message)


class DeletingTaskError(AppError):
    """
        This class describe error which appear when user try to add task
        """
    def __init__(self, message):
        message = ''.join(['Deleting task error: ', message])
        super().__init__(message)


class ActivationTaskError(AppError):
    """
    This class describe error which appear when user try to activate task
    """
    def __init__(self, message):
        message = ''.join(['Activation task error: ', message])
        super().__init__(message)


class TaskStatusError(AppError):
    """
    This class describe error which appear when user try to change
    status of task
    """
    def __init__(self, message):
        message = ''.join(['Task status error: ', message])
        super().__init__(message)


class TaskDeadlineError(AppError):
    """
    This class describe error which appear when user try to set incorrect
     task deadline
    """
    def __init__(self, message):
        message = ''.join(['Deadline error: ', message])
        super().__init__(message)
