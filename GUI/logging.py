import logging

# handles console logging
class Handler(logging.StreamHandler):
    def __init__(self, window):
        logging.StreamHandler.__init__(self)
        self.buffer = ""
        self.window = window

    def emit(self, record):
        self.format(record)
        record = f"{record.asctime} [{record.levelname}] {record.message}"
        self.buffer = f"{self.buffer}\n{record}".strip()
        try:
            self.window["log"].update(value=self.buffer)
        except: # GUI closed while running tasks
            pass
        
def setupConsoleLogging(mainWindow):
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="log.txt",
        filemode="a"
    )
    handler = Handler(mainWindow)
    logger = logging.getLogger("")
    logger.addHandler(handler)