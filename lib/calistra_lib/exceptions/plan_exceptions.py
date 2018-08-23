from .base_exception import AppError


class PlanNotFoundError(AppError):
    def __init__(self, message):
        message = ''.join(['Plan not found: ', message])
        super().__init__(message)
