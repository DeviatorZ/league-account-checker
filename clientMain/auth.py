import time
from clientMain.connection import RiotConnection
from exceptions import AuthenticationException
from exceptions import AccountBannedException
from exceptions import SessionException

def acceptEULA(riotConnection):
    riotConnection.put('/eula/v1/agreement/acceptance')

    
def authenticate(riotConnection, username, password):
    data = {"username": username, "password": password, 'persistLogin': False}
    response = riotConnection.put("/rso-auth/v1/session/credentials", json=data)
    
    responseJson = response.json()
        
    if responseJson["error"]:
        return responseJson
    return "OK"


def login(username, password, riotClientPath, lock):
    riotConnection = RiotConnection(riotClientPath, lock)

    authSuccess = authenticate(riotConnection, username, password)
    if not authSuccess == "OK":
        raise AuthenticationException(authSuccess["error"].upper(), riotConnection)

    acceptEULA(riotConnection)

    return riotConnection

def waitForLaunch(riotConnection, timeout=30):
    startTime = time.time()

    while True:
        phase = riotConnection.get('/rnet-lifecycle/v1/product-context-phase').json()

        if phase == "WaitForLaunch":
            return
        
        if time.time() - startTime >= timeout:
            raise SessionException("Launch timed out", riotConnection)
        time.sleep(1)

def waitForSession(leagueConnection, timeout=60):
    startTime = time.time()

    while True:
        session = leagueConnection.get('/lol-login/v1/session')
        session = session.json()

        if session["state"] == "ERROR":
            if session["error"]["messageId"] == "ACCOUNT_BANNED":
                raise AccountBannedException(session["error"], leagueConnection)
            if session["error"]["messageId"] == "FAILED_TO_COMMUNICATE_WITH_LOGIN_QUEUE":
                raise SessionException("Session exception", leagueConnection)
        elif session["state"] == "SUCCEEDED":
            time.sleep(1)
            return
        
        if time.time() - startTime >= timeout:
            raise SessionException("Session timed out", leagueConnection)
        time.sleep(1)