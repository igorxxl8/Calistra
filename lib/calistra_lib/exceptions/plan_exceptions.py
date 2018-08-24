"""
This module contains plans errors
"""

from .base_exception import AppError


class PlanNotFoundError(AppError):
    """
    This class using when user try to find plan whick doesn't exists
    """
    def __init__(self, message):
        message = ''.join(['Plan not found: ', message])
        super().__init__(message)
