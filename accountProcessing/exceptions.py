class RateLimitedException(Exception):
    def __init__(self, message):
        self.message = f"RateLimitedException - {message}"
        Exception.__init__(self)

class GracefulExit(Exception):
    def __init__(self):
        Exception.__init__(self)