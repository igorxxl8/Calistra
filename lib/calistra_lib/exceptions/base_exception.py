"""This module contains base error, from it inherits all
other program errors
"""

class AppError(Exception):
    """
    This class represent base type of program error
    """
    def __init__(self, message):
        self.message = ''.join(['calistra: ', message, '\n'])
        super().__init__(message)

    def __str__(self):
        return self.message
