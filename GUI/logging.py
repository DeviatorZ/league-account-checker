import logging
import PySimpleGUI as sg

class Handler(logging.StreamHandler):
    def __init__(self, logTextBox: sg.Multiline) -> None:
        """
        Custom logging handler that updates a PySimpleGUI Multiline element with log messages.

        :param logTextBox: The Multiline element to update with log messages.
        """
        logging.StreamHandler.__init__(self)
        self.__textBox = logTextBox

    def emit(self, record: logging.LogRecord) -> None:
        """
        Updates the Text element with the log message.

        :param record: The log record to emit.
        """
        self.format(record)
        record = f"{record.asctime} [{record.levelname}] {record.message}"
        try:
            self.__textBox.update(value=record.strip() + "\n", append=True)
        except: # GUI closed while running tasks
            pass
        
def setupConsoleLogging(logTextBox: sg.Multiline) -> None:
    """
    Sets up console logging for the application.

    :param logTextBox: The Multiline element to update with log messages.
    """
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="log.txt",
        filemode="a"
    )
    handler = Handler(logTextBox)
    logger = logging.getLogger("")
    logger.addHandler(handler)