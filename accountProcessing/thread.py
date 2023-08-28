from client.connection.exceptions import ConnectionException
from client.connection.exceptions import SessionException
from client.tasks.export import exportRaw
from accountProcessing.skipping import checkCanSkip
from accountProcessing.exceptions import RateLimitedException
from accountProcessing.exceptions import GracefulExit
from client.connection.exceptions import LaunchFailedException
from accountProcessing.LeagueOfLegendsWorker import LeagueOfLegendsWorker
from multiprocessing import Queue, Value, Event, Lock
from typing import Dict, Any
from accountProcessing.Progress import Progress
from client.leagueStore.exceptions import StoreException
from captcha.exceptions import CaptchaException
import time
import logging
import config

class Worker:
    def __init__(self, account: Dict[str, Any], settings: Dict[str, Any], progress: Progress, exitFlag: Event, allowPatching: bool, headless: bool, portQueue: Queue, nextRiotLaunch: Value, riotLock: Lock, nextLeagueLaunch: Value, leagueLock: Lock) -> None:
        """
        Initializes a Worker instance.

        :param account: Account information.
        :param setting: Worker settings.
        :param progress: Progress object for tracking completed tasks.
        :param exitFlag: Event flag for graceful exit.
        :param allowPatching: Flag indicating whether patching is allowed.
        :param headless: Flag indicating whether to run the client headless or not.
        :param portQueue: Queue for managing ports.
        :param nextRiotLaunch: Shared value for tracking next Riot client launch time.
        :param riotLock: Lock for accessing/modifying nextRiotLaunch.
        :param nextLeagueLaunch: Shared value for tracking next League client launch time.
        :param leagueLock: Lock for accessing/modifying nextLeagueLaunch.
        """
        self.__account = account
        self.__settings = settings
        self.__progress = progress
        self.__exitFlag = exitFlag
        self.__allowPatching = allowPatching
        self.__portQueue = portQueue
        self.__nextRiotLaunch = nextRiotLaunch
        self.__riotLock = riotLock
        self.__nextLeagueLaunch = nextLeagueLaunch
        self.__leagueLock = leagueLock
        self.__riotPort = self.__portQueue.get()
        self.__leaguePort = self.__portQueue.get()
        self.__headless = headless

    def __earlyExitCheck(self) -> None:
        """
        Checks if the exit flag is set and exits if necessary.
        """
        if self.__exitFlag.is_set():
            self.__exit(False)

    def __sleep(self, duration: float) -> None:
        """
        Sleeps for the specified duration while checking for early exit.

        :param duration: The duration in seconds to sleep.
        """
        while duration > 0:
            time.sleep(0.1)
            duration -= 0.1
            self.__earlyExitCheck()
    
    def __getNewPorts(self) -> None:
        """
        Replaces riot and league ports with new ones.
        """
        self.__portQueue.put(self.__riotPort)
        self.__portQueue.put(self.__leaguePort)
        self.__riotPort = self.__portQueue.get()
        self.__leaguePort = self.__portQueue.get()

    def run(self) -> None:
        """
        Executes tasks on a given account.
        """
        self.__earlyExitCheck()  
        if checkCanSkip(self.__settings, self.__account):
            self.__exit(True, export=False)

        failCount = 0
        rateLimitCount = 0

        logging.info("Executing tasks on account: " + self.__account["username"])
        while True:
            try:
                self.__earlyExitCheck()
                self.__getNewPorts()
                with LeagueOfLegendsWorker(self.__account, self.__settings, self.__allowPatching, self.__headless, self.__riotPort, self.__leaguePort) as leagueWorker:
                    self.__obtainRiotClientPermission()
                    status = leagueWorker.handleRiotClient()
                    if status != "OK":
                        if status == "AUTH_FAILURE":
                            self.__authFailure()
                        self.__exit(True)
                    self.__earlyExitCheck()

                    self.__obtainLeagueClientPermission()
                    status = leagueWorker.handleLeagueClient()
                    if status != "OK":
                        self.__exit(True)
                    self.__earlyExitCheck()

                    leagueWorker.performTasks()

                self.__account["state"] = "OK"
                self.__exit(True)
            except RateLimitedException as exception: # rate limited, wait before trying again
                rateLimitCount += 1
                if rateLimitCount >= config.MAX_RATE_LIMITED_ATTEMPTS:
                    self.__handleFailure()
                
                logging.error(f"{self.__account['username']} {exception.message}. Waiting before retrying...")
                self.__rateLimited(rateLimitCount)
            except (ConnectionException, SessionException, StoreException) as exception: # something went wrong with api
                logging.error(f"{self.__account['username']} {exception.message}. Retrying...")

                failCount += 1
                if failCount >= config.MAX_FAILED_ATTEMPTS:
                    self.__handleFailure()
                
                self.__sleep(1)
            except GracefulExit:
                self.__exit(False)
            except LaunchFailedException as exception:
                logging.error(f"Failed to launch {exception.className}. Make sure the path is correct.")
                logging.error(exception.error)
                self.__sleep(1)
            except CaptchaException as exception:
                logging.error("Failed to get Captcha token. Retrying...")
                self.__sleep(1)
            except Exception as exception:
                logging.error("Unhandled exception. Contact developer! Retrying...")
                logging.error(exception)
                self.__sleep(5)

    def __obtainRiotClientPermission(self) -> None:
        """
        Obtains permission to launch the Riot client.

        This method checks the next Riot client launch time stored in 'nextRiotLaunch' and sleeps if necessary until the launch cooldown is over.
        Once the cooldown is over, it updates the next launch time and returns.
        """
        while True:
            sleepTime = 0

            with self.__riotLock:
                currentTime = time.time()
                sleepTime = self.__nextRiotLaunch.value - currentTime

                if sleepTime <= 0:
                    self.__nextRiotLaunch.value = currentTime + config.RIOT_CLIENT_LAUNCH_COOLDOWN
                    return
                
            self.__sleep(sleepTime)

    def __obtainLeagueClientPermission(self) -> None:
        """
        Obtains permission to launch the League client.

        This method checks the next League client launch time stored in 'nextLeagueLaunch' and sleeps if necessary until the launch cooldown is over.
        Once the cooldown is over, it updates the next launch time and returns.
        """
        while True:
            sleepTime = 0

            with self.__leagueLock:
                currentTime = time.time()
                sleepTime = self.__nextLeagueLaunch.value - currentTime

                if sleepTime <= 0:
                    self.__nextLeagueLaunch.value = currentTime + config.LEAGUE_CLIENT_LAUNCH_COOLDOWN
                    return
                
            self.__sleep(sleepTime)

    def __rateLimited(self, rateLimitCount) -> None:
        """
        Handles getting rate limited.

        This method updates the nextRiotLaunch based on the launch cooldown specified for rate limited in the configuration.
        """
        with self.__riotLock:
            self.__nextRiotLaunch.value = time.time() + config.RATE_LIMITED_COOLDOWN * rateLimitCount

    def __authFailure(self) -> None:
        """
        Handles the authentication failure.

        This method updates the nextRiotLaunch based on the launch cooldown specified for invalid credentials in the configuration.
        """
        with self.__riotLock:
            self.__nextRiotLaunch.value = time.time() + config.LAUNCH_COOLDOWN_ON_INVALID_CREDENTIALS

    def __handleFailure(self) -> None:
        """
        Handles failure when too many attempts have been made.
        """
        logging.error(f"Too many failed attempts on account: {self.__account['username']}. Skipping...")
        self.__account["state"] = "RETRY_LIMIT_EXCEEDED"
        self.__exit(True)

    def __exit(self, finished: bool, export: bool = True) -> None:
        """
        Exit the worker.

        :param finished: Indicates whether the execution has finished.
        :param export: Indicates whether to export the account datas.
        """
        self.__portQueue.put(self.__riotPort)
        self.__portQueue.put(self.__leaguePort)
        if finished:
            if export:
                exportRaw(self.__account)
            self.__progress.add()
        raise GracefulExit

def runWorker(account: Dict[str, Any], settings: Dict[str, Any], progress: Progress, exitFlag: Event, allowPatching: bool, headless: bool, portQueue: Queue, nextRiotLaunch: Value, riotLock: Lock, nextLeagueLaunch: Value, leagueLock: Lock) -> None:
    """
    Initializes a Worker instance and runs it.
    """
    try:
        worker = Worker(account, settings, progress, exitFlag, allowPatching, headless, portQueue, nextRiotLaunch, riotLock, nextLeagueLaunch, leagueLock)
        worker.run()
    except GracefulExit:
        return
 