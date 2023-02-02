class ConnectionException(Exception):
    def __init__(self, connection):
        connection.__del__()
        Exception.__init__(self)

class AccountBannedException(Exception):
    def __init__(self, message, connection):
        self.message = message
        connection.__del__()
        Exception.__init__(self)

class SessionException(Exception):
    def __init__(self, message, connection):
        self.message = message
        connection.__del__()
        Exception.__init__(self)

class AuthenticationException(Exception):
    def __init__(self, message, connection):
        self.message = message
        connection.__del__()
        Exception.__init__(self)

class InvalidPathException(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self)