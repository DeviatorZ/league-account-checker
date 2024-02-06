from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import AuthenticationException
from client.connection.exceptions import SessionException
from client.connection.exceptions import LaunchFailedException
from client.version import getFileVersion
from captcha.exceptions import CaptchaException
from captcha.CaptchaProxy import CaptchaProxy
import time
import logging
from typing import Optional, Dict, Any
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

        version, success = getFileVersion(self.__path)
        if not success:
            raise LaunchFailedException(self.__class__.__name__, version)
        self.__userAgent = f"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) RiotClient/{version} (CEF 74) Safari/537.36"

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

    def __waitForConnection(self) -> Dict[str, Any]:
        """
        Used to authorize the connection.
        """
        data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}

        for _ in range(config.RIOT_CLIENT_LOADING_RETRY_COUNT):
            try:
                return self.post("/rso-auth/v2/authorizations", json=data).json()
            except ConnectionException:
                time.sleep(config.RIOT_CLIENT_LOADING_RETRY_COOLDOWN)

        return self.post("/rso-auth/v2/authorizations", json=data).json()


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

    def __authenticate(self, username: str, password: str, settings: Dict[str, Any]) -> str:
        """
        Authenticates with the client.
        """
        self.delete("/rso-authenticator/v1/authentication") # Make sure to log out if already logged in

        startAuthJson = self.post("/rso-authenticator/v1/authentication/riot-identity/start", json={"language":"en_GB","productId":"riot-client","state":"auth"}).json()

        captchaToken = CaptchaProxy.solve(
            settings,
            startAuthJson["captcha"]["hcaptcha"]["key"],
            startAuthJson["captcha"]["hcaptcha"]["data"],
            self.__userAgent,
        )

        authJson = {
            "username": username,
            "password": password,
            'persistLogin': False,
            "remember": False,
            "language": "en_GB",
            "captcha": f'hcaptcha {captchaToken}',
        }

        finishAuth = self.post("/rso-authenticator/v1/authentication/riot-identity/complete", json=authJson).json()
        if finishAuth["type"] != "success": # something went wrong
            return finishAuth["error"].upper()

        loginJson = {"authentication_type":"RiotAuth","login_token":finishAuth["success"]["login_token"], 'persistLogin': False,}
        self.put("/rso-auth/v1/session/login-token", json=loginJson)
        loginStatus = self.__waitForConnection()
        if loginStatus["type"] == "needs_authentication":
            raise AuthenticationException("RATE_LIMITED")

        return "OK"

    def __waitForLaunch(self, timeout: int = 30) -> None:
        """
        Waits until the client is ready to launch the League client.
        """
        startTime = time.time()

        while True:
            phase = self.get("/rnet-lifecycle/v1/product-context-phase").json()
            if phase == "Eula" or phase == "WaitingForEula":
                self.__acceptEULA()
            elif phase == "VngAccountRequired":
                raise AuthenticationException("VNG_ACCOUNT_REQUIRED")
            elif phase == "AccountAlias":
                raise AuthenticationException("NAME_CHANGE_REQUIRED")
            elif phase == "RiotIdRequired":
                raise AuthenticationException("RIOT_ID_REQUIRED")
            elif phase == "WaitForLaunch": # league client is ready for launch
                time.sleep(2)
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

    def login(self, username: str, password: str, settings: Dict[str, Any]) -> None:
        """
        Authenticates and prepares to launch the League client.
        """
        authSuccess = self.__authenticate(username, password, settings)
        if authSuccess == "CAPTCHA_NOT_ALLOWED":
            raise CaptchaException("Captcha not allowed!")
        elif not authSuccess == "OK": # something went wrong during login
            raise AuthenticationException(authSuccess)

        self.__waitForLaunch()
