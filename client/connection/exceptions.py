class RequestException(Exception):
    def __init__(self, message):
        self.message = f"RequestException - {message}"
        Exception.__init__(self)

class ConnectionException(Exception):
    def __init__(self, connection, message=None):
        self.connectionName = connection.__class__.__name__
        if message is None:
            self.message = f"{self.connectionName} - Connection failure"
        else:
            self.message = f"{self.connectionName}:{message}"
        connection.__del__()
        Exception.__init__(self)

class AuthenticationException(Exception):
    def __init__(self, connection, error):
        self.error = error
        connection.__del__()
        Exception.__init__(self)

class SessionException(Exception):
    def __init__(self, connection, message):
        self.connectionName = connection.__class__.__name__
        self.message = f"{self.connectionName}:SessionException - {message}"
        connection.__del__()
        Exception.__init__(self)

class AccountBannedException(Exception):
    def __init__(self, connection, error):
        self.error = error
        connection.__del__()
        Exception.__init__(self)