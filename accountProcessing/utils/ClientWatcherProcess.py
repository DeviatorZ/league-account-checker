from typing import List
from multiprocessing import Lock, Process
import psutil
import logging
from time import sleep
import config


class ClientWatcherProcess(Process):
    __PROCESSES_TO_KILL = {"RiotClientServices.exe", "LeagueClient.exe"}

    def __init__(self, portsInUse: List, lock: Lock):
        super().__init__()
        self.__portsInUse = portsInUse
        self.__lock = lock

    def run(self):
        while True:
            for process in psutil.process_iter(["pid", "name", "cmdline"]):
                if process.info["name"] in self.__PROCESSES_TO_KILL:
                    try:
                        cmdLineArgs = process.info["cmdline"]
                        if self.__canTerminate(cmdLineArgs):
                            logging.debug(f"Terminating process {process.info['pid']} ({cmdLineArgs[0]})")
                            psutil.Process(process.info["pid"]).terminate()
                    except Exception as e:
                        logging.debug(f"Error terminating a process: {e}")

            sleep(config.CLIENT_WATCHER_CHECK_COOLDOWN)

    def __canTerminate(self, cmdLineArgs):
        for arg in cmdLineArgs:
            if arg.startswith("--app-port"):
                _, value = arg.split("=")
                with self.__lock:
                    if int(value) in self.__portsInUse:
                        return False
                return True

        return True
