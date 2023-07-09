from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import AuthenticationException
from client.connection.exceptions import SessionException
import time
import logging
from typing import Optional, Dict
import requests
import config

class RiotConnection(Connection):
    def __init__(self, path: str, port: int, allowPatching: bool) -> None:
        """
        Initializes a RiotConnection instance.

        :param path: The path to the Riot client executable.
        :param port: The port number to use for the Riot client connection.
        :param allowPatching: Flag indicating whether to allow patching or not.
        """
        self.__allowPatching = allowPatching
        self.__path = path
        
        Connection.__init__(self, port)
        self.__getClient()
        self.__waitForConnection()

        time.sleep(1)

    def __getClient(self) -> None:
        """
        Launches the Riot client.

        Raises:
            LaunchFailedException: If launching the client application process fails.
        """
        processArgs = [
            self.__path,
            # specify our own port and token so we can connect to api
            "--app-port=" + self._port,
            "--remoting-auth-token=" + self._authToken,
            "--launch-product=league_of_legends",
            "--launch-patchline=live",
            "--locale=en_GB",
            "--disable-auto-launch", # disables automatic launch after logging in so we can launch league client with our own arguments
            "--headless",
        ]

        if not self.__allowPatching:
            processArgs.append("--allow-multiple-clients")

        Connection.getClient(self, processArgs)

    def getCredentials(self) -> Dict[str, str]:
        """
        Returns Riot client credentials.

        :return: A dictionary containing the Riot client port and authentication token.
        """
        return {"riotPort" : self._port, "riotAuthToken" : self._authToken}

    def __waitForConnection(self) -> None:
        """
        Used to authorize the connection.
        """
        data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}

        for _ in range(config.RIOT_CLIENT_LOADING_RETRY_COUNT):
            try:
                self.post("/rso-auth/v2/authorizations", json=data)
                return
            except ConnectionException:
                time.sleep(config.RIOT_CLIENT_LOADING_RETRY_COOLDOWN)

        self.post("/rso-auth/v2/authorizations", json=data)

    
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

            if response is None:
                raise RequestException(f"{method} : {url} : Retry limit exceeded")
            
            if response.ok:
                return response
            
            # RSO session failure
            if url == "/rso-auth/v1/session/credentials" and response.status_code == 400:
                return None

            raise RequestException(f"{method} : {url} : {response.status_code}")
        except RequestException as e:
            raise ConnectionException(self.__class__.__name__, e.message)
        except requests.exceptions.RequestException:
            raise ConnectionException(self.__class__.__name__)
        
    def __acceptEULA(self) -> None:
        """
        Accepts the End User License Agreement (EULA).
        """
        self.put("/eula/v1/agreement/acceptance")

    def __authenticate(self, username: str, password: str) -> str:
        """
        Authenticates with the client.

        :param username: The username to authenticate with.
        :param password: The password to authenticate with.

        Raises:
            AuthenticationException: If there is an issue with the authentication request.

        :return: "OK" if authentication succeeded, otherwise an error message.
        """
        data = {"username": username, "password": password, 'persistLogin': False}
        response = self.put("/rso-auth/v1/session/credentials", json=data)

        if response is None:
            raise AuthenticationException("CREDENTIALS_400")

        responseJson = response.json()
            
        if responseJson["error"]: # something went wrong during login
            return responseJson
        return "OK"
    
    def __waitForLaunch(self, timeout: int = 30) -> None:
        """
        Waits until the client is ready to launch the League client.

        :param timeout: The maximum time in seconds to wait for the launch.

        Raises:
            AuthenticationException: If the account requires email/phone number update.
            SessionException: If the launch preparation takes too long.
        """
        startTime = time.time()

        while True:
            phase = self.get("/rnet-lifecycle/v1/product-context-phase").json()
            if phase == "Eula" or phase == "WaitingForEula":
                self.__acceptEULA()
            elif phase == "VngAccountRequired":
                raise AuthenticationException(phase)
            elif phase == "WaitForLaunch": # league client is ready for launch
                time.sleep(1)
                return
            elif phase == "PatchStatus": # updating
                if not self.__allowPatching:
                    return
                logging.info("Waiting for RiotClient to update...")
                for _ in range(7200): # 2 hours
                    time.sleep(1)
                    phase = self.get("/rnet-lifecycle/v1/product-context-phase").json()
                    if phase != "PatchStatus":
                        startTime = time.time()
                        logging.info("Update finished!")
                        break
            if time.time() - startTime >= timeout: # took too long for launching to be ready
                raise SessionException(self.__class__.__name__, "League client launch timed out")
            time.sleep(1)

    def login(self, username: str, password: str) -> None:
        """
        Authenticates and prepares to launch the League client.

        :param username: The username to authenticate with.
        :param password: The password to authenticate with.
        :raises AuthenticationException: If the authentication fails.
        :raises SessionException: If the launch preparation takes too long.
        """
        authSuccess = self.__authenticate(username, password)
        if not authSuccess == "OK": # something went wrong during login
            raise AuthenticationException(authSuccess["error"].upper())

        self.__waitForLaunch()
