class RequestException(Exception):
    def __init__(self, message):
        self.message = f"RequestException - {message}"
        Exception.__init__(self)

class ConnectionException(Exception):
    def __init__(self, className, message=None):
        if message is None:
            self.message = f"{className} - Connection failure"
        else:
            self.message = f"{className}:{message}"
        Exception.__init__(self)

class AuthenticationException(Exception):
    def __init__(self, error):
        self.error = error
        Exception.__init__(self)

class SessionException(Exception):
    def __init__(self, className, message):
        self.message = f"{className}:SessionException - {message}"
        Exception.__init__(self)

class AccountBannedException(Exception):
    def __init__(self, error):
        self.error = error
        Exception.__init__(self)

class LaunchFailedException(Exception):
    def __init__(self, className, error):
        self.className = className
        self.error = error
        Exception.__init__(self)