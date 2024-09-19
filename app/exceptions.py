class InvalidFileError(Exception):
    def __init__(self, *args, details=None):
        self.details = details
        super().__init__(*args)


class NotFoundError(Exception):
    def __init__(self, *args, details=None):
        self.details = details
        super().__init__(*args)
