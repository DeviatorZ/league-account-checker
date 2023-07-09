class StoreException(Exception):
    def __init__(self, message):
        self.message = f"LoLStoreException: {message}"
        Exception.__init__(self)