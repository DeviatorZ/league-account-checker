from contextlib import contextmanager
from typing import List
from multiprocessing import Lock
from accountProcessing.utils.ClientWatcherProcess import ClientWatcherProcess


@contextmanager
def conditionalClientWatcher(portsInUse: List, lock: Lock, runWatcher: bool) -> None:
    watcher = None
    if runWatcher:
        watcher = ClientWatcherProcess(portsInUse, lock)
        watcher.start()

    try:
        yield
    finally:
        if watcher is not None:
            watcher.terminate()
            watcher.join()
