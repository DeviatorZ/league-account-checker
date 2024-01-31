class NoAccountDataException(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self)
