from threading import Thread
from threading import Event
from accountProcessing.run import executeAllAccounts
from client.tasks.export import eraseFiles
from client.tasks.export import exportAccounts
from GUI.layouts import *
from GUI.logging import setupConsoleLogging
from GUI.saving import *
from GUI.update import updateInformation
from GUI.userInputValidation import *
from GUI.exceptions import InvalidPathException
import copy
import PySimpleGUI as sg
import logging
import os
import config
from typing import Dict, Any

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

def setupGUI(cwd: str) -> sg.Window:
    """
    Sets up the GUI window.

    :param cwd: The current working directory.
    :return: The main window object.
    """
    sg.theme("Black")
    sg.user_settings_filename("settings.json", path=f"data")

    layout = [
        [sg.TabGroup([[
            sg.Tab("Main", getMainLayout()), 
            sg.Tab("Settings", getSettingsLayout(cwd)),
            sg.Tab("Tasks", getTasksLayout()),
            sg.Tab("Export", getExportLayout()),
            sg.Tab("Refunds", getRefundsLayout()),
        ]])],
    ]

    mainWindow = sg.Window("DeviatorZ Account Checker", layout, font=("Helvetica", 15), finalize=True) # create the window
    mainWindow["log"].update(disabled=True) # disable typing in logging console

    setupConsoleLogging(mainWindow["log"])

    return mainWindow

def runGUI(mainWindow: sg.Window) -> None:
    """
    Runs the GUI event loop.

    :param mainWindow: The main window object.
    """
    exitEvent = Event()

    # event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = mainWindow.read()
        if event == sg.WIN_CLOSED: # if user closes window
            exitEvent.set() # set event to gracefully exit all checker threads
            break
        elif event == "start":
            exitEvent.clear()
            Thread(target=execute, args=(copy.deepcopy(values), mainWindow, exitEvent)).start()
        elif event == "stop":
            exitEvent.set()
        elif event == "saveSettings":
            saveSettings(values)
        elif event == "saveTasks":
            saveTasks(values)
        elif event == "saveRefunds":
            saveRefunds(values)
        elif event == "deleteRaw":
            logging.info("Deleting raw data...")
            eraseFiles(config.RAW_DATA_PATH)
            logging.info("Raw data erased!")
        elif event == "exportNow":
            exportAccounts(values["bannedTemplate"], values["errorTemplate"], values["failedSeparately"])
        elif event == "openExports":
            try:
                os.startfile(config.EXPORT_PATH)
            except:
                pass
        elif event == "saveExport":
            saveExport(values)
        elif event == "updateInformation":
            Thread(target=updateInformation, args=[mainWindow["updateInformation"]]).start()

    mainWindow.close()