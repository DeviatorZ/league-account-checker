from multiprocessing.pool import ThreadPool
from datetime import datetime
from clientMain.connection import RiotConnection
from clientMain.connection import LeagueConnection
from clientMain.auth import login
from clientMain.auth import waitForSession
from exceptions import *
from clientTasks.export import exportAccounts
from clientTasks.data import getData
from clientMain.loot import Loot
import time
import os
import csv
import json

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

def checkForFileErrors(settings):
    if not os.path.exists(settings["riotClient"]):
        raise InvalidPathException("RiotClientServices.exe path doesn't exist!")

    if not os.path.exists(settings["leagueClient"]):
        raise InvalidPathException("LeagueClient.exe path doesn't exist!")

    if not os.path.exists(settings["accountsFile"]):
        raise InvalidPathException("Account file path doesn't exist!")

def execute(account, settings, lock, logger, progress):
    try:
        executeAccount(account, settings, lock, logger)
        progress.add()
    except ConnectionException:
        logger.error(f"{account['username']} connection exception. Retrying...")
        execute(account, settings, lock, logger, progress)
        


def executeAccount(account, settings, lock, logger):
    logger.info("Executing tasks on account: " + account["username"])
    
    try:
        riotConnection = login(account["username"], account["password"], settings["riotClient"], lock)
    except AuthenticationException as exception:
        logger.error(f"{account['username']} login exception: {exception.message}")
        account["state"] = exception.message
        return 

    region = riotConnection.get("/riotclient/region-locale")
    region = region.json()
    account["region"] = region["region"]

    leagueConnection = LeagueConnection(settings["leagueClient"], riotConnection, account["region"], lock)

    try:
        waitForSession(leagueConnection)
    except SessionException as exception:
        logger.error(f"{account['username']} session exception: {exception.message}. Retrying...")
        return executeAccount(account, settings, lock, logger)
    except AccountBannedException as ban:
        banDescription = json.loads(ban.message['description'])
        account["state"] = "BANNED"
        account["banReason"] = banDescription["restrictions"][0]["reason"]
        if banDescription["restrictions"][0]["type"] != "PERMANENT_BAN":
            banExpiration = banDescription["restrictions"][0]["dat"]["expirationMillis"]
            account["banExpiration"] = datetime.utcfromtimestamp(banExpiration / 1000).strftime('%Y-%m-%d %Hh%Mm%Ss')
        else:
            account["banExpiration"] = "PERMANENT"

        logger.error(f"{account['username']} banned exception: Reason:{account['banReason']}, Expiration:{account['banExpiration']}")
        return 

    loot = Loot(leagueConnection)
    
    if not settings["exportMin"]:
        getData(leagueConnection, account, loot)

    leagueConnection.__del__()
    account["state"] = "OK"
    return 

def executeAllAccounts(settings, lock, logger, progressBar):
    try:
        checkForFileErrors(settings)
    except InvalidPathException as exception:
        logger.error(exception.message)
        return

    accounts = []

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
        logger.error(f"Account file format error. Expected line format: username{settings['accountsDelimiter']}password")
        return
    except SyntaxError as error:
        logger.error(error.msg)
        return

    progress = Progress(len(accounts), progressBar)
    pool = ThreadPool(processes=int(settings["threadCount"]))
    args = [[account, settings, lock, logger, progress] for account in accounts]

    with pool:
        pool.starmap(execute, args)

    logger.info("Exporting accounts")
    exportAccounts(accounts, settings["bannedTemplate"], settings["errorTemplate"])
    logger.info("All tasks completed!")