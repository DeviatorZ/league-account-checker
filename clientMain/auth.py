import time
from clientMain.connection import RiotConnection
from exceptions import AuthenticationException
from exceptions import AccountBannedException
from exceptions import SessionException

# accepts eula, needed on new accounts or when eula gets changed
def acceptEULA(riotConnection):
    riotConnection.put('/eula/v1/agreement/acceptance')

# tries to login on riot client
# returns "OK" if auth succeeded, error otherwise
def authenticate(riotConnection, username, password):
    data = {"username": username, "password": password, 'persistLogin': False}
    response = riotConnection.put("/rso-auth/v1/session/credentials", json=data)
    
    responseJson = response.json()
        
    if responseJson["error"]: # something went wrong during login
        return responseJson
    return "OK"

# launches riot client, tries to authenticate, handles authentication errors, accepts eula
# returns riot client object
def login(username, password, riotClientPath, lock):
    riotConnection = RiotConnection(riotClientPath, lock)

    authSuccess = authenticate(riotConnection, username, password)
    if not authSuccess == "OK": # something went wrong during login
        raise AuthenticationException(authSuccess["error"].upper(), riotConnection)

    acceptEULA(riotConnection)

    return riotConnection

# waits until riot client is ready to launch league client
# raises an exception if it takes too long
def waitForLaunch(riotConnection, timeout=30):
    startTime = time.time()

    while True:
        phase = riotConnection.get('/rnet-lifecycle/v1/product-context-phase').json()

        if phase == "WaitForLaunch": # league client is ready for launch
            return
        
        if time.time() - startTime >= timeout: # took too long for launching to be ready
            raise SessionException("Launch timed out", riotConnection)
        time.sleep(1)

# waits until league client finishes loading a session (lcu api can't be used until it's done)
# raises an exception if an account is banned, if communication failed with login queue or if it took to long
def waitForSession(leagueConnection, timeout=60):
    startTime = time.time()

    while True:
        session = leagueConnection.get('/lol-login/v1/session')
        session = session.json()

        if session["state"] == "ERROR":
            if session["error"]["messageId"] == "ACCOUNT_BANNED": # account is banned
                raise AccountBannedException(session["error"], leagueConnection)
            if session["error"]["messageId"] == "FAILED_TO_COMMUNICATE_WITH_LOGIN_QUEUE": # something went wrong while loading the session (possibly rate limited?)
                raise SessionException("Failed to communicate with login queue", leagueConnection)
        elif session["state"] == "SUCCEEDED": # successfully loaded the session
            time.sleep(2)
            return
        
        if time.time() - startTime >= timeout: # session took too long to load
            raise SessionException("Session timed out", leagueConnection)
        time.sleep(1)