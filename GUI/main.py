from threading import Thread
from threading import Event
from accountProcessing.threadHandler import executeAllAccounts
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

# validates user input and launches tasks
def execute(settings, lock, mainWindow, exitEvent):
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
    
    executeAllAccounts(settings, accounts, lock, mainWindow["progress"], exitEvent)
    
    try:
        mainWindow["start"].update(disabled=False)
        mainWindow["deleteRaw"].update(disabled=False)
    except: # GUI closed while running tasks
        pass

def setupGUI(cwd):
    sg.theme("Black")
    sg.user_settings_filename("settings.json", path=f"data")

    layout = [
        [sg.TabGroup([[
            sg.Tab("Main", getMainLayout()), 
            sg.Tab("Settings", getSettingsLayout(cwd)),
            sg.Tab("Tasks", getTasksLayout()),
            sg.Tab("Export", getExportLayout()),
        ]])],
    ]

    mainWindow = sg.Window("DeviatorZ Account Checker", layout, font=("Helvetica", 15), finalize=True) # create the window
    mainWindow["log"].update(disabled=True) # disable typing in logging console

    setupConsoleLogging(mainWindow)

    return mainWindow

def runGUI(mainWindow, cwd, lock):
    exitEvent = Event()

    # event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = mainWindow.read()
        if event == sg.WIN_CLOSED: # if user closes window
            exitEvent.set() # set event to gracefully exit all checker threads
            break
        elif event == "start":
            exitEvent.clear()
            Thread(target=execute, args=(copy.deepcopy(values), lock, mainWindow, exitEvent)).start()
        elif event == "stop":
            exitEvent.set()
        elif event == "saveSettings":
            saveSettings(values)
        elif event == "saveTasks":
            saveTasks(values)
        elif event == "deleteRaw":
            eraseFiles("data\\raw")
            logging.info("Raw exports erased!")
        elif event == "exportNow":
            exportAccounts(values["bannedTemplate"], values["errorTemplate"])
        elif event == "openExports":
            try:
                os.startfile(f"{cwd}\\export")
            except:
                pass
        elif event == "saveExport":
            saveExport(values)
        elif event == "updateInformation":
            Thread(target=updateInformation, args=[mainWindow]).start()

    mainWindow.close()