from requests import Session
from requests import adapters
import urllib3
import subprocess
from client.connection.credentials import getAuthToken
from client.connection.exceptions import LaunchFailedException
from typing import List
import logging
import requests

class Connection(Session):
    """
    Custom class for Riot and League clients' connection.

    This class extends the `Session` class from the `requests` library to handle API requests to the client.
    """
    def __init__(self, port: int) -> None:
        """
        Initializes the Connection class with the specified port.

        :param port: The port number used for the client connection.
        """
        self._port = str(port)
        self._url = "https://127.0.0.1:" + self._port
        self._authToken = getAuthToken()
        self._process = None
        Session.__init__(self)
        retry = urllib3.util.retry.Retry(
            total = 4,
            respect_retry_after_header = True,
            status_forcelist = [429, 404, 500],
            backoff_factor = 1
        )

        adapter = adapters.HTTPAdapter(max_retries=retry)
        self.mount("https://", adapter)
        urllib3.disable_warnings()

    def request(self, method: str, url: str, *args, **kwargs) -> Session.request:
        """
        Sends an API request to the client.

        :return: The API response.
        """      
        try:
            logging.debug(f"{method} : {url} : {args} {kwargs}")
        except Exception as e:
            logging.debug(e)
            
        url = self._url + url
        # Setup Riot authentication
        kwargs["auth"] = "riot", self._authToken
        kwargs["verify"] = False

        try:
            response = Session.request(self, method, url, *args, **kwargs)
        except requests.exceptions.RetryError as e:
            logging.debug(e)
            return None

        try:
            logging.debug(f"{response.status_code} : {response.text}")
        except Exception as e:
            logging.debug(e)

        return response
    
    def getClient(self, processArgs: List[str]) -> None:
        """
        Opens a process for the client application with the given arguments.

        :param processArgs: The arguments for the client application process.

        Raises:
            LaunchFailedException: If launching the client application process fails.
        """
        while True:
            try:
                self._process = subprocess.Popen(processArgs)
                return
            except OSError as error:
                raise LaunchFailedException(self.__class__.__name__, error)
    
    def kill(self) -> None:
        """
        Terminates the client process.
        """
        if self._process is not None:
            self._process.terminate()
    
    