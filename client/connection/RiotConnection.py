from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import AuthenticationException
from client.connection.exceptions import SessionException
import time
import logging

# handles riot client and it's api
class RiotConnection(Connection):
    def __init__(self, path, lock, allowPatching):
        # start a riot client and wait for connection to avoid port conflicts and api rate limits
        self.__allowPatching = allowPatching
        self.__path = path
        
        with lock:
            Connection.__init__(self)
            self.__getClient()
            self.__waitForConnection()

        time.sleep(1)

    # launch riot client with our own command line arguments
    def __getClient(self):
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

    # returns riot port and auth token (needed for league client)
    def getCredentials(self):
        return {"riotPort" : self._port, "riotAuthToken" : self._authToken}

    # used to wait for response before removing lock and API authentication
    def __waitForConnection(self):
        data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}
        self.post("/rso-auth/v2/authorizations", json=data)

    # handles api requests to the client
    # raises ConnectionException if the request fails
    def request(self, method, url, *args, **kwargs):
        # handle api request, make sure the request is successful - raise a ConnectionException if it isn't
        try:
            response = Connection.request(self, method, url, *args, **kwargs)
            
            # RSO session failure
            if url == "/rso-auth/v1/session/credentials" and response.status_code == 400:
                return None
            
            if response.ok:
                return response

            raise RequestException(f"{method} : {url} : {response.status_code}")
        except RequestException as e:
            raise ConnectionException(self, e.message)
        except Exception:
            raise ConnectionException(self)
        
    # accepts eula, needed on new accounts or when eula gets changed
    def __acceptEULA(self):
        self.put("/eula/v1/agreement/acceptance")

    # tries to login
    # returns "OK" if auth succeeded, error otherwise
    def __authenticate(self, username, password):
        data = {"username": username, "password": password, 'persistLogin': False}
        response = self.put("/rso-auth/v1/session/credentials", json=data)

        if response is None:
            raise AuthenticationException(self, "CREDENTIALS_400")

        responseJson = response.json()
            
        if responseJson["error"]: # something went wrong during login
            return responseJson
        return "OK"
    
    # waits until riot client is ready to launch league client
    # raises AuthenticationException if the account requires email/phone number update
    # raises SessionException if it takes too long
    def __waitForLaunch(self, timeout=30):
        startTime = time.time()

        while True:
            phase = self.get('/rnet-lifecycle/v1/product-context-phase').json()
            if phase == "Eula" or phase == "WaitingForEula":
                self.__acceptEULA()
            elif phase == "VngAccountRequired":
                raise AuthenticationException(self, phase)
            elif phase == "WaitForLaunch": # league client is ready for launch
                time.sleep(1)
                return
            elif phase == "PatchStatus": # updating
                logging.info("Waiting for RiotClient to update...")
                for _ in range(7200): # 2 hours
                    time.sleep(1)
                    phase = self.get('/rnet-lifecycle/v1/product-context-phase').json()
                    if phase != "PatchStatus":
                        startTime = time.time()
                        logging.info("Update finished!")
                        break
            if time.time() - startTime >= timeout: # took too long for launching to be ready
                raise SessionException(self, "League client launch timed out")
            time.sleep(1)

    # authenticates and prepares to launch league client
    # raises AuthenticationException if it fails
    # raises SessionException if launch preparation takes too long
    def login(self, username, password):
        authSuccess = self.__authenticate(username, password)
        if not authSuccess == "OK": # something went wrong during login
            raise AuthenticationException(self, authSuccess["error"].upper())

        self.__waitForLaunch()
