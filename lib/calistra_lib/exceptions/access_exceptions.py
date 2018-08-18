from .base_exception import AppError


class AccessDeniedError(AppError):
    def __init__(self, message):
        message = ''.join(['Access denied: ', message])
        super().__init__(message)
