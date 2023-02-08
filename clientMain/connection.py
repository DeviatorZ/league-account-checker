from requests import Session
from requests import adapters
import urllib3
import subprocess
from time import sleep
from clientMain.credentials import getFreePort
from clientMain.credentials import getAuthToken
from exceptions import ConnectionException
# Send requests to Riot and League clients, requires auth token and port

# inherited class for riot and league clients
class Connection(Session):
    def __init__(self):
        # use our own port and auth token so we can connect to api while running headless
        self.port = str(getFreePort())
        self.url = "https://127.0.0.1:" + self.port
        self.authToken = getAuthToken()
        Session.__init__(self)
        retry = urllib3.util.retry.Retry(
            total = 5,
            respect_retry_after_header = True,
            status_forcelist = [429, 404],
            backoff_factor = 2
        )

        adapter = adapters.HTTPAdapter(max_retries=retry)
        self.mount("https://", adapter)
        urllib3.disable_warnings()

    # handles api requests to the client
    def request(self, method, url, *args, **kwargs):
        url = self.url + url
        # setup riot authentication
        kwargs["auth"] = "riot", self.authToken
        kwargs["verify"] = False
        
        # handle api request, make sure the request is successful - raise an exception if it isn't
        try:
            response = Session.request(self, method, url, *args, **kwargs)
            if response.ok:
                return response
            raise Exception
        except Exception:
            raise ConnectionException(self)
    
    # opens a process (league/riot client) with given arguments
    def getClient(self, processArgs):
        while True:
            try:
                self.process = subprocess.Popen(processArgs)
                return
            except:
                sleep(1)
    
    # terminates client process 
    def __del__(self):
        self.process.terminate()
        self.process.wait()

# handles riot client and it's api
class RiotConnection(Connection):
    def __init__(self, path, lock):
        # start a riot client and wait for connection to avoid port conflicts and api rate limits
        with lock:
            Connection.__init__(self)
            self.path = path
            self.getClient()
            self.waitForConnection()

    # launch riot client with our own command line arguments
    def getClient(self):
        processArgs = [
            self.path,
            # specify our own port and token so we can connect to api
            "--app-port=" + self.port,
            "--remoting-auth-token=" + self.authToken,
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
        return {"riotPort" : self.port, "riotAuthToken" : self.authToken}


    def waitForConnection(self):
        data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}
        self.post("/rso-auth/v2/authorizations", json=data)

# handles league client and it's api
class LeagueConnection(Connection):
    def __init__(self, path, riotConnection, region, lock):
        # start a league client and wait for connection to avoid port conflicts and api rate limits
        with lock:
            Connection.__init__(self)
            self.path = path
            self.riotConnection = riotConnection
            self.riotCredentials = riotConnection.getCredentials()
            self.region = region
            self.getClient()
            self.waitForConnection()

    # launch league client with our own command line arguments
    def getClient(self):
        processArgs = [
            self.path,
            # specify riot client port and auth token that has an account logged in
            "--riotclient-app-port=" + self.riotCredentials["riotPort"],
            "--riotclient-auth-token=" + self.riotCredentials["riotAuthToken"],
            # specify our own port and token for league client so we can connect to api
            "--app-port=" + self.port,
            "--remoting-auth-token=" + self.authToken,
            "--allow-multiple-clients", 
            "--locale=en_GB",
            "--disable-self-update",
            "--region=" + self.region, # region of the account logged in on riot client (league client session fails without this)
            "--headless"
        ]

        Connection.getClient(self, processArgs)

    def waitForConnection(self):
        self.get('/lol-login/v1/session')

    # terminates league client and then riot client
    def __del__(self):
        Connection.__del__(self)
        self.riotConnection.__del__()
    
    