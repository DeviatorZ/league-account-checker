from requests import Session
from requests import adapters
import urllib3
import subprocess
from time import sleep
from client.connection.credentials import getFreePort
from client.connection.credentials import getAuthToken

# inherited class for riot and league clients
class Connection(Session):
    def __init__(self):
        # use our own port and auth token so we can connect to api while running headless
        self._port = str(getFreePort())
        self._url = "https://127.0.0.1:" + self._port
        self._authToken = getAuthToken()
        Session.__init__(self)
        retry = urllib3.util.retry.Retry(
            total = 6,
            respect_retry_after_header = True,
            status_forcelist = [429, 404, 500],
            backoff_factor = 1
        )

        adapter = adapters.HTTPAdapter(max_retries=retry)
        self.mount("https://", adapter)
        urllib3.disable_warnings()

    # handles api requests to the client
    def request(self, method, url, *args, **kwargs):
        url = self._url + url
        # setup riot authentication
        kwargs["auth"] = "riot", self._authToken
        kwargs["verify"] = False
        
        # return api request
        return Session.request(self, method, url, *args, **kwargs)
    
    # opens a process (league/riot client) with given arguments
    def getClient(self, processArgs):
        while True:
            try:
                self._process = subprocess.Popen(processArgs)
                return
            except:
                sleep(1)
    
    # terminates client process 
    def __del__(self):
        self._process.terminate()
    
    