from client.connection.exceptions import ConnectionException
from client.connection.exceptions import SessionException
from client.tasks.export import exportRaw
from accountProcessing.skipping import checkCanSkip
from accountProcessing.exceptions import RateLimitedException
from accountProcessing.exceptions import GracefulExit
from client.connection.exceptions import LaunchFailedException
from accountProcessing.LeagueOfLegendsWorker import LeagueOfLegendsWorker
from accountProcessing.utils.PortHandler import PortHandler
from accountProcessing.utils.PortManager import PortManager
from multiprocessing import Value, Event, Lock
from typing import Dict, Any
from accountProcessing.Progress import Progress
from client.leagueStore.exceptions import StoreException
from captcha.exceptions import CaptchaException
import time
import logging
import config
import traceback


class Worker:

    def __init__(self, account: Dict[str, Any], settings: Dict[str, Any], progress: Progress, exitFlag: Event, allowPatching: bool, headless: bool, portHandler: PortHandler, nextRiotLaunch: Value, riotLock: Lock, nextLeagueLaunch: Value, leagueLock: Lock) -> None:
        """
        Initializes a Worker instance.
        """
        self.__account = account
        self.__settings = settings
        self.__progress = progress
        self.__exitFlag = exitFlag
        self.__allowPatching = allowPatching
        self.__portManager = PortManager(portHandler)
        self.__nextRiotLaunch = nextRiotLaunch
        self.__riotLock = riotLock
        self.__nextLeagueLaunch = nextLeagueLaunch
        self.__leagueLock = leagueLock
        self.__headless = headless
        self.__failCount = 0
        self.__rateLimitCount = 0

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

    def run(self) -> None:
        """
        Executes tasks on a given account.
        """
        self.__earlyExitCheck()  
        if checkCanSkip(self.__settings, self.__account):
            self.__exit(True, export=False)

        self.__failCount = 0
        self.__rateLimitCount = 0

        logging.info("Executing tasks on account: " + self.__account["username"])
        while True:
            try:
                self.__earlyExitCheck()
                with self.__portManager as ports:
                    with LeagueOfLegendsWorker(
                        self.__account,
                        self.__settings,
                        self.__allowPatching,
                        self.__headless,
                        ports.getRiotPort(),
                        ports.getLeaguePort(),
                    ) as leagueWorker:
                        self.__obtainRiotClientPermission()
                        status = leagueWorker.handleRiotClient()
                        if status != "OK":
                            if status == "AUTH_FAILURE":
                                self.__authFailure()
                            self.__exit(True, status)
                        self.__earlyExitCheck()

                        self.__obtainLeagueClientPermission()
                        status = leagueWorker.handleLeagueClient()
                        if status != "OK":
                            self.__exit(True, status)
                        self.__earlyExitCheck()

                        leagueWorker.performTasks()

                self.__exit(True)
            except RateLimitedException as exception: # rate limited, wait before trying again
                self.__handleRateLimited(exception)
            except (ConnectionException, StoreException) as exception: # something went wrong with api
                self.__handleGeneralException(exception)
            except SessionException as exception:
                if exception.error == "Failed to communicate with login queue":
                    region = self.__account["region"]
                    logging.info(f"{self.__account['username']} {region} region account can't be ran on current client patch or the server is down. Skipping...")
                    self.__exit(True, "CLIENT_PATCHING_REQUIRED")
                self.__handleGeneralException(exception)
            except GracefulExit:
                self.__exit(False)
            except LaunchFailedException as exception:
                logging.error(f"Failed to launch {exception.className}. Make sure the path is correct.")
                logging.error(exception.error)
                self.__sleep(1)
            except CaptchaException as exception:
                logging.error(f"{self.__account['username']} {exception.message} Retrying...")
                self.__sleep(1)
            except Exception:                                  
                logging.error(traceback.format_exc())
                logging.error("Unhandled exception. Contact developer! Retrying...")
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

    def __handleRateLimited(self, exception: RateLimitedException) -> None:
        self.__rateLimitCount += 1
        with self.__riotLock:
            self.__nextRiotLaunch.value = time.time() + config.RATE_LIMITED_COOLDOWN * self.__rateLimitCount

        if self.__rateLimitCount >= config.MAX_RATE_LIMITED_ATTEMPTS:
            logging.error(f"{self.__account['username']} {exception.message}.")
            self.__handleFailure()
        else:
            logging.error(f"{self.__account['username']} {exception.message}. Waiting before retrying...")

    def __handleGeneralException(self, exception: Exception) -> None:
        self.__failCount += 1
        if self.__failCount >= config.MAX_FAILED_ATTEMPTS:
            logging.error(f"{self.__account['username']} {exception.message}.")
            self.__handleFailure()
        else:
            logging.error(f"{self.__account['username']} {exception.message}. Retrying...")

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
        self.__exit(True, "RETRY_LIMIT_EXCEEDED")

    def __exit(self, finished: bool, state: str = "OK", export: bool = True,) -> None:
        """
        Exit the worker.
        """
        if finished:
            if export:
                self.__account["state"] = state
                exportRaw(self.__account)
            self.__progress.add()
        raise GracefulExit


def runWorker(account: Dict[str, Any], settings: Dict[str, Any], progress: Progress, exitFlag: Event, allowPatching: bool, headless: bool, portHandler: PortHandler, nextRiotLaunch: Value, riotLock: Lock, nextLeagueLaunch: Value, leagueLock: Lock) -> None:
    """
    Initializes a Worker instance and runs it.
    """
    try:
        worker = Worker(account, settings, progress, exitFlag, allowPatching, headless, portHandler, nextRiotLaunch, riotLock, nextLeagueLaunch, leagueLock)
        worker.run()
    except GracefulExit:
        return
