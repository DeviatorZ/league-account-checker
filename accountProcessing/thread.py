from client.connection.RiotConnection import RiotConnection
from client.connection.LeagueConnection import LeagueConnection
from client.connection.exceptions import ConnectionException
from client.connection.exceptions import AuthenticationException
from client.connection.exceptions import SessionException
from client.connection.exceptions import AccountBannedException
from client.loot import Loot
from data.TaskList import TaskList
from client.tasks.data import getData
from accountProcessing.exceptions import RateLimitedException
from accountProcessing.exceptions import GracefulExit
from time import sleep
from datetime import datetime
import logging
import json

# check if exit flag has been set and quit early
def checkForGracefulExit(exitFlag, connection=None):
    if exitFlag.is_set():
        raise GracefulExit(connection)
    else:
        return False

# handles task execution on a given account
def execute(account, settings, lock, progress, exitFlag):   
    failCount = 0

    while True:
        try:
            checkForGracefulExit(exitFlag)

            executeAccount(account, settings, lock, exitFlag)

            if not checkForGracefulExit(exitFlag): # if graceful exit is triggered, no longer need to track progress
                progress.add()

            return
        except GracefulExit:
            return
        except RateLimitedException as exception: # rate limited, wait before trying again
            logging.error(f"{account['username']} {exception.message}. Waiting before retrying...")
            sleep(300)
        except (ConnectionException, SessionException) as exception: # something went wrong with api
            logging.error(f"{account['username']} {exception.message}. Retrying...")

            failCount += 1
            if failCount >= 5:
                logging.error(f"Too many failed attempts on account: {account['username']}. Skipping...")
                account["state"] = "RETRY_LIMIT_EXCEEDED"
                if not checkForGracefulExit(exitFlag): # if graceful exit is triggered, no longer need to track progress
                    progress.add()
                return

# performs tasks on a given account, check for graceful exit flag between tasks
def executeAccount(account, settings, lock, exitFlag):
    logging.info("Executing tasks on account: " + account["username"])

    riotConnection = handleRiotClient(account, settings, lock)

    if riotConnection is None:
        return
    
    checkForGracefulExit(exitFlag, riotConnection)
    
    leagueConnection = handleLeagueClient(account, settings, lock, riotConnection)

    if leagueConnection is None:
        return
    
    checkForGracefulExit(exitFlag, leagueConnection)

    loot = Loot(leagueConnection) # create loot object to use for all tasks on the account
    performTasks(leagueConnection, settings, loot)

    checkForGracefulExit(exitFlag, leagueConnection)

    # obtain extra account information if it's not set to minimal type
    if not settings["exportMin"]:
        getData(leagueConnection, account, loot)

    leagueConnection.__del__() # tasks finished, terminate clients
    account["state"] = "OK"

def handleRiotClient(account, settings, lock):
    riotConnection = RiotConnection(settings["riotClient"], lock)

    try:
        riotConnection.login(account["username"], account["password"])
        region = riotConnection.get("/riotclient/region-locale").json()
        account["region"] = region["region"] # region needed for league client
    except AuthenticationException as exception:
        if exception.error == "RATE_LIMITED": # rate limited due too many accounts with incorrect credentials
            raise RateLimitedException(riotConnection, "Too many login attempts")
        else: # wrong credentials / account needs updating
            logging.error(f"{account['username']} AuthenticationException: {exception.error}")
            account["state"] = exception.error
            riotConnection.__del__()
            return None
        
    return riotConnection

def handleLeagueClient(account, settings, lock, riotConnection):
    try:
        leagueConnection = LeagueConnection(settings["leagueClient"], riotConnection, account["region"], lock)
        leagueConnection.waitForSession()
    except AccountBannedException as ban:
        # add ban information to the account for export
        banDescription = json.loads(ban.error["description"])
        account["state"] = "BANNED"
        account["banReason"] = banDescription["restrictions"][0]["reason"]

        if banDescription["restrictions"][0]["type"] != "PERMANENT_BAN":
            banExpiration = banDescription["restrictions"][0]["dat"]["expirationMillis"]
            account["banExpiration"] = datetime.utcfromtimestamp(banExpiration / 1000).strftime('%Y-%m-%d %Hh%Mm%Ss') # banExpiration is unix timestamp in miliseconds
        else:
            account["banExpiration"] = "PERMANENT"

        logging.error(f"{account['username']} AccountBannedException - Reason:{account['banReason']}, Expiration:{account['banExpiration']}")
        return None
    
    return leagueConnection

def performTasks(leagueConnection, settings, loot):
    tasks = TaskList.getTasks(leagueConnection, loot)
    
    # run tasks
    for taskName, task in tasks.items():
        if settings[taskName]:
            task["function"](*task["args"])
            sleep(1) # allow loot to update between tasks