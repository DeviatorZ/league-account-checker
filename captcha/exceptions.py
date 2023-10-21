class CaptchaException(Exception):
    def __init__(self, message: str):
        self.message = message
        Exception.__init__(self)