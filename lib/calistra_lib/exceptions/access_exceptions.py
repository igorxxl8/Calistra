"""This module contains class AccessDeniedError for represent error
whick happend when user try to get access to someone else entity"""

from .base_exception import AppError


class AccessDeniedError(AppError):
    """
    Define error which appear when user try to get acess to someone else entity
    """
    def __init__(self, message):
        message = ''.join(['Access denied: ', message])
        super().__init__(message)
