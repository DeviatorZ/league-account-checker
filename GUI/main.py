from threading import Thread
from threading import Event
from client.tasks.export import exportAccounts
from GUI.layouts import *
from GUI.logging import setupConsoleLogging
from GUI.saving import *
from GUI.update import updateInformation
from GUI.championShop import *
from GUI.checker import execute
from GUI.export import exportInputAccounts, deleteRawData
import copy
import PySimpleGUI as sg
import os
import config
import webbrowser

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
            sg.Tab("Captcha", getCaptchaLayout()),
            sg.Tab("Data", getDatatLayout()),
            sg.Tab("Tasks", getTasksLayout()),
            sg.Tab("ChampionShop", getChampionShopLayout()),
            sg.Tab("Export", getExportLayout()),
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
        elif event == "saveChampionShop":
            saveChampionShop(values)
        elif event == "saveDataTab":
            saveData(values)
        elif event == "saveExport":
            saveExport(values)
        elif event == "deleteRaw":
            response = sg.popup_yes_no("Are you sure?")
            if response and response == "Yes":
                Thread(target=deleteRawData).start()
        elif event == "exportNow":
            Thread(target=exportAccounts, args=(values[guiKeys.BANNED_ACCOUNT_STATE_TEMPLATE], values[guiKeys.ERROR_ACCOUNT_STATE_TEMPLATE], values[guiKeys.EXPORT_FAILED_SEPARATELY])).start()
        elif event == "exportNowOnlyInput":    
            Thread(target=exportInputAccounts, args=(copy.deepcopy(values),)).start()
        elif event == "openExports":
            try:
                os.startfile(config.EXPORT_PATH)
            except:
                pass
        elif event == "updateInformation":
            Thread(target=updateInformation, args=(mainWindow["updateInformation"],)).start()
        elif event == "addChampion":
            addChampion(values, mainWindow[guiKeys.CHAMPION_SHOP_PURCHASE_LIST], mainWindow["championShopResponse"])
        elif event == "removeChampion":
            removeChampion(values, mainWindow[guiKeys.CHAMPION_SHOP_PURCHASE_LIST], mainWindow["championShopResponse"])
        elif event == "saveCaptcha":
            saveCaptcha(values)

    mainWindow.close()