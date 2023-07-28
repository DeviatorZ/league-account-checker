
from client.tasks.export import exportAccounts
from client.tasks.export import eraseFiles
from client.tasks.export import exportUnfinished
import PySimpleGUI as sg
import logging
from client.champions import Champions
from client.skins import Skins
from client.lootdata import LootData
import config
from typing import Any, Dict, List
from threading import Event
from accountProcessing.Executor import Executor

def preExecutionWork(settings: Dict[str, Any]) -> None:
    """
    Perform pre-execution tasks based on the provided settings.

    :param settings: Execution settings.
    """
    if settings["autoDeleteRaw"]:
            eraseFiles(config.RAW_DATA_PATH)
    Champions.refreshData(config.CHAMPION_FILE_PATH)
    Skins.refreshData(config.SKIN_FILE_PATH)
    LootData.refreshData(config.LOOT_DATA_FILE_PATH, config.LOOT_ITEMS_FILE_PATH)

def postExecutionWork(settings: Dict[str, Any], accounts: List[Dict[str, Any]]) -> None:
    """
    Perform post-execution tasks based on the provided settings.

    :param settings: Execution settings.
    :param accounts: The list of accounts that tasks were executed on.
    """
    if settings["autoExport"]:
        exportAccounts(settings["bannedTemplate"], settings["errorTemplate"], settings["failedSeparately"])
    exportUnfinished(accounts, settings["accountsDelimiter"])

def executeAllAccounts(settings: Dict[str, Any], accounts: List[Dict[str, Any]], progressBar: sg.Text, exitEvent: Event) -> None:
    """
    Executes tasks for all accounts.

    :param settings: Execution settings.
    :param accounts: The list of accounts to execute tasks on.
    :param progressBar: The progress bar object.
    :param exitEvent: The exit event to stop execution.
    """
    logging.info("Starting tasks...")
    preExecutionWork(settings)

    executor = Executor(settings, progressBar, exitEvent)
    executor.run(accounts)

    postExecutionWork(settings, accounts)
    logging.info("All tasks completed!")