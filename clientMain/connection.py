from requests import Session
from requests import adapters
import urllib3
import subprocess
from time import sleep
from clientMain.credentials import getFreePort
from clientMain.credentials import getAuthToken
from exceptions import ConnectionException
# Send requests to Riot and League clients, requires auth token and port

class Connection(Session):
    def __init__(self):
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

    def request(self, method, url, *args, **kwargs):
        url = self.url + url
        kwargs["auth"] = "riot", self.authToken
        kwargs["verify"] = False

        try:
            response = Session.request(self, method, url, *args, **kwargs)
            if response.ok:
                return response
            raise Exception
        except Exception:
            raise ConnectionException(self)
    
    def getClient(self, processArgs):
        while True:
            try:
                self.process = subprocess.Popen(processArgs)
                return
            except:
                sleep(1)
    
    def __del__(self):
        self.process.terminate()
        self.process.wait()

class RiotConnection(Connection):
    def __init__(self, path, lock):
        with lock:
            Connection.__init__(self)
            self.path = path
            self.getClient()
            self.waitForConnection()

    def getClient(self):
        processArgs = [
            self.path,
            "--app-port=" + self.port,
            "--remoting-auth-token=" + self.authToken,
            "--launch-product=league_of_legends",
            "--launch-patchline=live",
            "--allow-multiple-clients",
            "--locale=en_GB",
            "--disable-auto-launch",
            "--headless",
        ]

        Connection.getClient(self, processArgs)

    def getCredentials(self):
        return {"riotPort" : self.port, "riotAuthToken" : self.authToken}


    def waitForConnection(self):
        data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}
        self.post("/rso-auth/v2/authorizations", json=data)

class LeagueConnection(Connection):
    def __init__(self, path, riotConnection, region, lock):
        with lock:
            Connection.__init__(self)
            self.path = path
            self.riotConnection = riotConnection
            self.riotCredentials = riotConnection.getCredentials()
            self.region = region
            self.getClient()
            self.waitForConnection()

    def getClient(self):
        processArgs = [
            self.path,
            "--riotclient-app-port=" + self.riotCredentials["riotPort"],
            "--riotclient-auth-token=" + self.riotCredentials["riotAuthToken"],
            "--app-port=" + self.port,
            "--remoting-auth-token=" + self.authToken,
            "--allow-multiple-clients", 
            "--locale=en_GB",
            "--disable-self-update",
            "--region=" + self.region,
            "--headless"
        ]

        Connection.getClient(self, processArgs)

    def waitForConnection(self):
        self.get('/lol-login/v1/session')

    
    def __del__(self):
        Connection.__del__(self)
        self.riotConnection.__del__()
    
    