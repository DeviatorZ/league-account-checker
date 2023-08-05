from accountProcessing.run import executeAllAccounts
from GUI.exceptions import InvalidPathException, InvalidInputException
from typing import Dict, Any
import PySimpleGUI as sg
import logging
from GUI.userInputValidation import *
from threading import Event

def execute(settings: Dict[str, Any], mainWindow: sg.Window, exitEvent: Event) -> None:
    """
    Validates user input and launches tasks.

    :param settings: The user settings dictionary.
    :param mainWindow: The main window object.
    :param exitEvent: The event used to gracefully exit all checker threads.
    """
    try:
        checkForFileErrors(settings)
    except InvalidPathException as exception:
        logging.error(exception.message)
        return
    
    try:
        accounts = getAccounts(settings)
    except IndexError:
        logging.error(f"Account file format error. Expected line format: username{settings['accountsDelimiter']}password")
        return 
    except SyntaxError as error:
        logging.error(error.msg)
        return 

    try:
        validateChampionShop(settings)
    except InvalidInputException as exception:
        logging.error(exception.message)
        return

    try:
        mainWindow["start"].update(disabled=True)
        mainWindow["deleteRaw"].update(disabled=True)
    except: # GUI closed while running tasks
        return
    
    executeAllAccounts(settings, accounts, mainWindow["progress"], exitEvent)
    
    try:
        mainWindow["start"].update(disabled=False)
        mainWindow["deleteRaw"].update(disabled=False)
    except: # GUI closed while running tasks
        pass