class AppError(Exception):
    def __init__(self, message):
        self.message = ''.join(['calistra: ', message, '\n'])
        super().__init__(message)

    def __str__(self):
        return self.message
