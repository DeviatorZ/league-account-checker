from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import AuthenticationException
from client.connection.exceptions import SessionException
import time

# handles riot client and it's api
class RiotConnection(Connection):
    def __init__(self, path, lock):
        # start a riot client and wait for connection to avoid port conflicts and api rate limits
        with lock:
            Connection.__init__(self)
            self.__path = path
            self.__getClient()
            self.__waitForConnection()

    # launch riot client with our own command line arguments
    def __getClient(self):
        processArgs = [
            self.__path,
            # specify our own port and token so we can connect to api
            "--app-port=" + self._port,
            "--remoting-auth-token=" + self._authToken,
            "--launch-product=league_of_legends",
            "--launch-patchline=live",
            "--allow-multiple-clients",
            "--locale=en_GB",
            "--disable-auto-launch", # disables automatic launch after logging in so we can launch league client with our own arguments
            "--headless",
        ]

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
            if phase == "VngAccountRequired":
                raise AuthenticationException(self, phase)
            if phase == "WaitForLaunch": # league client is ready for launch
                time.sleep(1)
                return
            
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

        self.__acceptEULA()

        self.__waitForLaunch()
