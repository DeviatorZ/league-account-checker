from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import SessionException
from client.connection.exceptions import AccountBannedException
from client.connection.RiotConnection import RiotConnection
import time
import logging
import math
from typing import Optional
import requests

class LeagueConnection(Connection):
    def __init__(self, path: str, riotConnection: RiotConnection, region: str, port: int, allowPatching: bool) -> None:
        """
        Initializes a LeagueConnection instance.

        :param path: The path to the League client executable.
        :param riotConnection: The RiotConnection instance for interacting with the Riot client.
        :param region: The region of the account logged in on the Riot client.
        :param port: The port number to use for the League client connection.
        :param allowPatching: Flag indicating whether to allow patching or not.
        """
        self.__allowPatching = allowPatching
        self.__path = path
        self.__riotConnection = riotConnection
        self.__riotCredentials = self.__riotConnection.getCredentials()
        self.__region = region

        Connection.__init__(self, port)
        self.__getClient()
        self.__waitForConnection()

    def __getClient(self) -> None:
        """
        Launches the League client.
        
        Raises:
            LaunchFailedException: If launching the client application process fails.
        """
        processArgs = [
            self.__path,
            # specify riot client port and auth token that has an account logged in
            "--riotclient-app-port=" + self.__riotCredentials["riotPort"],
            "--riotclient-auth-token=" + self.__riotCredentials["riotAuthToken"],
            # specify our own port and token for league client so we can connect to api
            "--app-port=" + self._port,
            "--remoting-auth-token=" + self._authToken,
            "--locale=en_GB",
            "--region=" + self.__region, # region of the account logged in on riot client (league client session fails without this)
            "--headless"
        ]

        if not self.__allowPatching:
            processArgs.append("--allow-multiple-clients")
            processArgs.append("--disable-self-update")

        Connection.getClient(self, processArgs)

    def __waitForConnection(self) -> None:
        """
        Acts as a first request tester.
        """
        self.get("/lol-login/v1/session")

    def request(self, method: str, url: str, *args, **kwargs) -> Optional[requests.Response]:
        """
        Sends an API request to the client.

        :param method: The HTTP method of the request.
        :param url: The API endpoint URL.
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.

        Raises:
            ConnectionException: If the request fails.

        :return: The response object if the request is successful, None otherwise.
        """
        try:
            response = Connection.request(self, method, url, *args, **kwargs)

            if response and response.ok:
                return response
            
            # no token event is currently running
            if (url == "/lol-event-shop/v1/claim-select-all" or url == "/lol-event-shop/v1/categories-offers") and (response is None or not response.ok):
                return None
            
            if response is None:
                raise RequestException(f"{method} : {url} : Retry limit exceeded")
            
            # got a queue penalty
            if url == "/lol-lobby/v2/lobby/matchmaking/search" and response.status_code == 400:
                return None

            raise RequestException(f"{method} : {url} : {response.status_code}")
        except RequestException as e:
            raise ConnectionException(self.__class__.__name__, e.message)
        except requests.exceptions.RequestException:
            raise ConnectionException(self.__class__.__name__)
        
    def waitForSession(self, timeout: int = 60) -> None:
        """
        Waits until the client finishes loading a session.

        :param timeout: The maximum time to wait for the session to load.

        Raises:
            AccountBannedException: If the account is banned.
            SessionException: If the session loading takes too long or if login fails.
        """
        startTime = time.time()

        while True:
            session = self.get("/lol-login/v1/session")
            session = session.json()

            if session["state"] == "ERROR":
                if session["error"]["messageId"] == "ACCOUNT_BANNED": # account is banned
                    raise AccountBannedException(session["error"])
                if session["error"]["messageId"] == "FAILED_TO_COMMUNICATE_WITH_LOGIN_QUEUE": # something went wrong while loading the session
                    raise SessionException(self.__class__.__name__, "Failed to communicate with login queue")
            elif session["state"] == "SUCCEEDED": # successfully loaded the session
                time.sleep(2)
                return
            
            if time.time() - startTime >= timeout: # session took too long to load
                raise SessionException(self.__class__.__name__, "Session timed out")
            time.sleep(1)

    def waitForUpdate(self, timeout: int = 7200) -> None:
        """
        Waits for the client to finish patching.

        :param timeout: The maximum time to wait for the patching process to complete.

        Raises:
            SessionException: If the patching process takes too long.
        """
        if not self.__allowPatching:
            return
    
        startTime = time.time()
        currentAction = "Unknown"
        currentProgressPercent = -1

        while True:
            clientState = self.get("/lol-patch/v1/products/league_of_legends/state").json()

            action = clientState.get("action", "Unknown")
            if action == "Idle":
                if currentAction != "Unknown":
                    logging.info("Update finished!")
                return
            elif action != currentAction: # avoid repetition in logs
                currentAction = action
                logging.info(f"{currentAction} LeagueClient...")

            progress = clientState["components"][0]["progress"]["total"]
            progressPercent = math.floor(progress["bytesComplete"] / progress["bytesRequired"] * 100)

            if progressPercent != currentProgressPercent: # avoid repetition in logs
                currentProgressPercent = progressPercent
                logging.info(f"{currentProgressPercent}% completed.")

            if time.time() - startTime >= timeout: # update took too long
                raise SessionException(self.__class__.__name__, "Update timed out")
            time.sleep(1)

    def kill(self) -> None:
        """
        Terminates the League client and Riot client processes.
        """
        Connection.kill(self)
        self.__riotConnection.kill()