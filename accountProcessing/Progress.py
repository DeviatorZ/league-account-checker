from threading import Lock
import PySimpleGUI as sg

class Progress():
    def __init__(self, total: int, progressBar: sg.Text):
        """
        Initialize the Progress class.

        :param total: The total count of items to track.
        :param progressBar: The progress bar object.
        """
        self.__total = total
        self.__counter = 0
        self.__progressBar = progressBar
        self.__lock = Lock()
        self.__update()

    def add(self) -> None:
        """
        Increments the counter and updates the progress.
        """
        with self.__lock:
            self.__counter += 1
            self.__update()

    def __update(self) -> None:
        """
        Updates the progress bar with the current counter value.
        """
        self.__progressBar.update(f"Completed {self.__counter}/{self.__total} accounts")