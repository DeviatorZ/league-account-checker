from client.connection.Connection import Connection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import RequestException
from client.connection.exceptions import SessionException
from client.connection.exceptions import AccountBannedException
import time
import logging
import math

# handles league client and it"s api
class LeagueConnection(Connection):
    def __init__(self, path, riotConnection, region, lock, allowPatching):
        # start a league client and wait for connection to avoid port conflicts and api rate limits
        self.__allowPatching = allowPatching
        self.__path = path
        self.__riotConnection = riotConnection
        self.__riotCredentials = self.__riotConnection.getCredentials()
        self.__region = region

        with lock:
            Connection.__init__(self)
            self.__getClient()
            self.__waitForConnection()

    # launch league client with our own command line arguments
    def __getClient(self):
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

    # used to wait for response before removing lock
    def __waitForConnection(self):
        self.get("/lol-login/v1/session")

    # handles api requests to the client
    # raises ConnectionException if the request fails
    def request(self, method, url, *args, **kwargs):
        # handle api request, make sure the request is successful - raise a ConnectionException if it isn"t
        try:
            response = Connection.request(self, method, url, *args, **kwargs)
            if response.ok:
                return response

            # no token event is currently running
            if (url == "/lol-event-shop/v1/claim-select-all" or url == "/lol-event-shop/v1/categories-offers") and not response.ok:
                return None
            
            # got a queue penalty
            if url == "/lol-lobby/v2/lobby/matchmaking/search" and response.status_code == 400:
                return None

            raise RequestException(f"{method} : {url} : {response.status_code}")
        except RequestException as e:
            raise ConnectionException(self, e.message)
        except Exception:
            raise ConnectionException(self)
        
    # waits until league client finishes loading a session (lcu api can"t be used until it"s done)
    # raises AccountBannedException if the account is banned
    # raises SessionException if it took too long or if login failed
    def waitForSession(self, timeout=60):
        startTime = time.time()

        while True:
            session = self.get("/lol-login/v1/session")
            session = session.json()

            if session["state"] == "ERROR":
                if session["error"]["messageId"] == "ACCOUNT_BANNED": # account is banned
                    raise AccountBannedException(self, session["error"])
                if session["error"]["messageId"] == "FAILED_TO_COMMUNICATE_WITH_LOGIN_QUEUE": # something went wrong while loading the session
                    raise SessionException(self, "Failed to communicate with login queue")
            elif session["state"] == "SUCCEEDED": # successfully loaded the session
                time.sleep(2)
                return
            
            if time.time() - startTime >= timeout: # session took too long to load
                raise SessionException(self, "Session timed out")
            time.sleep(1)

    # waits for league client to finish patching
    # raises SessionException if it took too long
    def waitForUpdate(self, timeout=7200):
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
                raise SessionException(self, "Update timed out")
            time.sleep(1)

    # terminates league client and then riot client
    def __del__(self):
        Connection.__del__(self)
        self.__riotConnection.__del__()