from multiprocessing.pool import ThreadPool
from multiprocessing import Manager
from client.tasks.export import exportAccounts
from accountProcessing.thread import execute
from time import sleep
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

# handles checking threads
def executeAllAccounts(settings, accounts, lock, progressBar, exitEvent):

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