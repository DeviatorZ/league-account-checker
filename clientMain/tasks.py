from multiprocessing.pool import ThreadPool
from multiprocessing import Manager 
from datetime import datetime
from clientMain.connection import RiotConnection
from clientMain.connection import LeagueConnection
from clientMain.auth import login
from clientMain.auth import waitForSession
from clientMain.auth import waitForLaunch
from exceptions import *
from clientTasks.export import exportAccounts
from clientTasks.data import getData
from clientTasks.event import claimEventRewards
from clientTasks.event import buyChampionShardsWithTokens
from clientTasks.event import buyBlueEssenceWithTokens
from clientTasks.crafting import craftKeys
from clientTasks.crafting import openChests
from clientTasks.crafting import openLoot
from clientTasks.disenchanting import disenchantChampionShards
from clientTasks.disenchanting import disenchantEternalsShards
from clientMain.loot import Loot
from TaskList import TaskList
from time import sleep
import os
import csv
import json
import logging

# class for tracking checking progress
class Progress():
    def __init__(self, total, progressBar):
        self.total = total
        self.counter = 0
        self.progressBar = progressBar
        self.update()

    def add(self):
        self.counter += 1
        self.update()

    def update(self):
        self.progressBar.update(f"Completed {self.counter}/{self.total} accounts")  

# make sure user input files exist
def checkForFileErrors(settings):
    if not os.path.exists(settings["riotClient"]):
        raise InvalidPathException("RiotClientServices.exe path doesn't exist!")

    if not os.path.exists(settings["leagueClient"]):
        raise InvalidPathException("LeagueClient.exe path doesn't exist!")

    if not os.path.exists(settings["accountsFile"]):
        raise InvalidPathException("Account file path doesn't exist!")

# tries executing tasks on a given account and adjusts progress bar if it's successful, retries otherwise
def execute(account, settings, lock, progress, exitFlag): 
    if exitFlag.is_set():
        return
    
    try:
        executeAccount(account, settings, lock, exitFlag)
        if not exitFlag.is_set():
            progress.add()
    except ConnectionException as exception:
        logging.error(f"{account['username']} {exception.connectionName} exception. Retrying...")
        execute(account, settings, lock, progress, exitFlag)

# performs tasks on a given account
def executeAccount(account, settings, lock, exitFlag):
    logging.info("Executing tasks on account: " + account["username"])

    riotConnection = RiotConnection(settings["riotClient"], lock)

    # login to riot client, handle authentication exception
    try:
        login(account["username"], account["password"], riotConnection)
        region = riotConnection.get("/riotclient/region-locale").json()
        account["region"] = region["region"]
        waitForLaunch(riotConnection)
    except AuthenticationException as exception:
        if exception.message == "RATE_LIMITED":
            logging.error(f"{account['username']} login exception: {exception.message}. Waiting before retrying...")
            sleep(300)
            return executeAccount(account, settings, lock, exitFlag)
        else:
            logging.error(f"{account['username']} login exception: {exception.message}")
            account["state"] = exception.message
            return
    except SessionException as exception:
        logging.error(f"{account['username']} session exception: {exception.message}. Retrying...")
        return executeAccount(account, settings, lock, exitFlag)

    if exitFlag.is_set():
        riotConnection.__del__()
        return

    # get account region from riot client (required for league client)
    region = riotConnection.get("/riotclient/region-locale")
    region = region.json()
    account["region"] = region["region"]

    # launch league client and wait session, handle session and account ban exceptions
    try:
        waitForLaunch(riotConnection)
        leagueConnection = LeagueConnection(settings["leagueClient"], riotConnection, account["region"], lock)
        waitForSession(leagueConnection)
    except SessionException as exception:
        logging.error(f"{account['username']} session exception: {exception.message}. Retrying...")
        return executeAccount(account, settings, lock, exitFlag)
    except AccountBannedException as ban:
        # add ban information to the account for export
        banDescription = json.loads(ban.message["description"])
        account["state"] = "BANNED"
        account["banReason"] = banDescription["restrictions"][0]["reason"]
        if banDescription["restrictions"][0]["type"] != "PERMANENT_BAN":
            banExpiration = banDescription["restrictions"][0]["dat"]["expirationMillis"]
            account["banExpiration"] = datetime.utcfromtimestamp(banExpiration / 1000).strftime('%Y-%m-%d %Hh%Mm%Ss')
        else:
            account["banExpiration"] = "PERMANENT"

        logging.error(f"{account['username']} banned exception: Reason:{account['banReason']}, Expiration:{account['banExpiration']}")
        return
    
    if exitFlag.is_set():
        leagueConnection.__del__()
        return

    loot = Loot(leagueConnection) # create loot object to use for all tasks on the account
    performTasks(leagueConnection, settings, loot)

    # obtain extra account information if it's not set to minimal type
    if not settings["exportMin"]:
        getData(leagueConnection, account, loot)

    leagueConnection.__del__() # tasks finished, terminate league and riot clients
    account["state"] = "OK"

def performTasks(leagueConnection, settings, loot):
    tasks = TaskList.getTasks(leagueConnection, loot)
    
    # run tasks
    for taskName, task in tasks.items():
        if settings[taskName]:
            task["function"](*task["args"])
            sleep(1)

# launches tasks on accounts
def executeAllAccounts(settings, lock, progressBar, exitEvent):
    try:
        checkForFileErrors(settings) # make sure user input files exist
    except InvalidPathException as exception:
        logging.error(exception.message)
        return

    accounts = []

    # read account file
    try:
        with open(settings["accountsFile"]) as csvfile:
            reader = csv.reader(csvfile, delimiter=settings["accountsDelimiter"])
            for index, row in enumerate(reader, start=1):
                if row[0] == "":
                    raise SyntaxError("Missing username in account file - Line " + str(index))
                elif row[1] == "":
                    raise SyntaxError("Missing password in account file - Line " + str(index))
                accounts.append({
                    "username" : row[0],
                    "password" : row[1],
                })
    except IndexError:
        logging.error(f"Account file format error. Expected line format: username{settings['accountsDelimiter']}password")
        return
    except SyntaxError as error:
        logging.error(error.msg)
        return

    with Manager() as manager:
        progress = Progress(len(accounts), progressBar) # create progress handler
        exitFlag = manager.Event()
        args = [(account, settings, lock, progress, exitFlag) for account in accounts] # create function args for every account

        with ThreadPool(processes=int(settings["threadCount"])) as pool:
            results = pool.starmap_async(execute, args)
            while not results.ready():
                if exitEvent.is_set():
                    logging.info("Stopping execution...")
                    exitFlag.set()
                    pool.close()
                    pool.join()
                    logging.info("Execution stopped!")
                    return
                sleep(1)
        
    logging.info("Exporting accounts")
    exportAccounts(accounts, settings["bannedTemplate"], settings["errorTemplate"]) # export all accounts after tasks are finished
    logging.info("All tasks completed!")