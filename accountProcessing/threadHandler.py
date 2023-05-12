from multiprocessing.pool import ThreadPool
from multiprocessing import Manager
from client.tasks.export import exportAccounts
from client.tasks.export import eraseFiles
from client.tasks.export import exportUnfinished
from accountProcessing.thread import runWorker
from client.connection.credentials import getFreePorts
from accountProcessing.Progress import Progress
from time import sleep
import logging
from client.champions import Champions
from client.skins import Skins
import config
from typing import Any, Dict, List
from threading import Event

def preExecutionWork(settings: Dict[str, Any]) -> None:
    """
    Perform pre-execution tasks based on the provided settings.

    :param settings: Execution settings.
    """
    if settings["autoDeleteRaw"]:
            eraseFiles("data\\raw")
    Champions.refreshData(config.CHAMPION_FILE_PATH)
    Skins.refreshData(config.SKIN_FILE_PATH)

def postExecutionWork(settings: Dict[str, Any], accounts: List[Dict[str, Any]]) -> None:
    """
    Perform post-execution tasks based on the provided settings.

    :param settings: Execution settings.
    """
    if settings["autoExport"]:
        exportAccounts(settings["bannedTemplate"], settings["errorTemplate"], settings["failedSeparately"])
    exportUnfinished(accounts, settings["accountsDelimiter"])

def executeAllAccounts(settings: Dict[str, Any], accounts: List[Dict[str, Any]], progressBar: Progress, exitEvent: Event) -> None:
    """
    Execute tasks for all accounts.

    :param settings: Execution settings.
    :param accounts: The list of accounts to execute tasks on.
    :param progressBar: The progress bar object.
    :param exitEvent: The exit event to stop execution.
    """
    preExecutionWork(settings)

    progress = Progress(len(accounts), progressBar)

    threadCount = int(settings["threadCount"])
    allowPatching = threadCount == 1

    with Manager() as manager:
        exitFlag = manager.Event()
        nextRiotLaunch = manager.Value("d", 0.0)
        riotLock = manager.Lock()
        nextLeagueLaunch = manager.Value("d", 0.0)
        leagueLock = manager.Lock()
        portQueue = manager.Queue()
        for port in getFreePorts(threadCount * 100):
            portQueue.put(port)
        args = [(account, settings, progress, exitFlag, allowPatching, portQueue, nextRiotLaunch, riotLock, nextLeagueLaunch, leagueLock) for account in accounts]
        with ThreadPool(processes=threadCount) as pool:
            results = pool.starmap_async(runWorker, args)
            while not results.ready():
                if exitEvent.is_set():
                    logging.info("Stopping execution...")
                    exitFlag.set()
                    pool.close()
                    pool.join()
                    logging.info("Execution stopped!")
                    break
                sleep(1)

    postExecutionWork(settings, accounts)
    logging.info("All tasks completed!")