class AppError(Exception):
    def __init__(self, message):
        message = ''.join(['calistra: ', message])
        super().__init__(message)
