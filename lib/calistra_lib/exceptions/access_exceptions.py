"""This module contains class AppError for represent main app error"""

from .base_exception import AppError


class AccessDeniedError(AppError):
    """
    Error
    """
    def __init__(self, message):
        message = ''.join(['Access denied: ', message])
        super().__init__(message)
