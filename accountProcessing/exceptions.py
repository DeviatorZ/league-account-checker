class RateLimitedException(Exception):
    def __init__(self, connection, message):
        self.connectionName = connection.__class__.__name__
        self.message = f"{self.connectionName}:RateLimitException - {message}"
        Exception.__init__(self)

class GracefulExit(Exception):
    def __init__(self, connection=None):
        if connection is not None:
            connection.__del__()
        Exception.__init__(self)