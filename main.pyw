from threading import Thread
from threading import Lock
from clientMain.tasks import executeAllAccounts
from clientTasks.export import eraseFiles
from update import update
from time import sleep
import subprocess
import copy
import PySimpleGUI as sg
import logging
import os

class Handler(logging.StreamHandler):
    def __init__(self, window):
        logging.StreamHandler.__init__(self)
        self.buffer = ""
        self.window = window

    def emit(self, record):
        self.format(record)
        record = f'{record.asctime} [{record.levelname}] {record.message}'
        self.buffer = f'{self.buffer}\n{record}'.strip()
        self.window['log'].update(value=self.buffer)


def execute(values, lock, mainWindow):
    thread = Thread(target=executeAllAccounts, args=(values, lock, mainWindow["progress"]))
    thread.start()
    thread.join()
    mainWindow["start"].update(disabled=False)
    mainWindow["eraseExports"].update(disabled=False)

def updateInformation(mainWindow):
    mainWindow["updateInformation"].update(disabled=True)
    thread = Thread(target=update, args=[mainWindow])
    thread.start()
    thread.join()
    mainWindow["updateInformation"].update(disabled=False)

def saveSettings(values):
    sg.user_settings_set_entry("riotClient", values["riotClient"])
    sg.user_settings_set_entry("leagueClient", values["leagueClient"])
    sg.user_settings_set_entry("accountsFile", values["accountsFile"])
    sg.user_settings_set_entry("accountsDelimiter", values["accountsDelimiter"])
    sg.user_settings_set_entry("threadCount", values["threadCount"])

def saveTasks(values):
    sg.user_settings_set_entry("craftKeys", values["craftKeys"])
    sg.user_settings_set_entry("openChests", values["openChests"])

def saveExport(values):
    sg.user_settings_set_entry("bannedTemplate", values["bannedTemplate"])
    sg.user_settings_set_entry("errorTemplate", values["errorTemplate"])
    sg.user_settings_set_entry("exportMin", values["exportMin"])


def main():
    lock = Lock()
    cwd = os.getcwd()
    sg.theme('Black')
    sg.user_settings_filename("settings.json", path=cwd)

    mainLayout = [
        [sg.Output(size=(110, 25), key="log", font=("Helvetica", 8))],
        [sg.Button("Start", key="start"), sg.Button("Open exports folder", key="openExports"), sg.Button("Erase exports", key="eraseExports"), sg.Text("", key="progress")] 
    ]

    settingsLayout = [
        [sg.Text("RiotClientServices.exe location")],
        [sg.Input(sg.user_settings_get_entry("riotClient", "C:\\Riot Games\\Riot Client\\RiotClientServices.exe"), key="riotClient"), sg.FileBrowse()],
        [sg.Text("LeagueClient.exe location")],
        [sg.Input(sg.user_settings_get_entry("leagueClient", "C:\\Riot Games\\League of Legends\\LeagueClient.exe"), key="leagueClient"), sg.FileBrowse()],
        [sg.Text("Account file location")],
        [sg.Input(sg.user_settings_get_entry("accountsFile", cwd + "\\accounts.csv"), key="accountsFile"), sg.FileBrowse()],
        [sg.Text("Account file delimiter"), sg.InputCombo((",",":",";"), default_value=sg.user_settings_get_entry("accountsDelimiter", ":"), key="accountsDelimiter")],
        [sg.Text("Thread count"), sg.Combo([x for x in range(1,11)], default_value=sg.user_settings_get_entry("threadCount", "2"), key="threadCount")],
        [sg.Button("Save", key="saveSettings")],
    ]

    tasksLayout = [
        [sg.Checkbox("Craft hextech keys", default=sg.user_settings_get_entry("craftKeys", True), key="craftKeys"),
        sg.Checkbox("Open hextech chests", default=sg.user_settings_get_entry("openChests", True), key="openChests")],
        [sg.Button("Save", key="saveTasks")],
    ]

    exportLayout = [
        [sg.Text("Banned account template")],
        [sg.Input(sg.user_settings_get_entry("bannedTemplate", "{username};{password};{region};{banReason} {banExpiration}"), key="bannedTemplate", size=60)],
        [sg.Text("Error account template")],
        [sg.Input(sg.user_settings_get_entry("errorTemplate", "{username};{password};{state}"), key="errorTemplate", size=60)],
        [sg.Text("Standard export type"), sg.Radio("Minimal", "export", default=sg.user_settings_get_entry("exportMin", False), key="exportMin"), 
        sg.Radio("Full", "export", default=not sg.user_settings_get_entry("exportMin", False))],
        [sg.Button("Save", key="saveExport")],
        [sg.VPush()],
        [sg.Button("Update skin and champion information", key="updateInformation"), sg.Text("", key="updateStatus")],
    ]

    layout = [
        [sg.TabGroup([[
            sg.Tab("Main", mainLayout), 
            sg.Tab("Settings", settingsLayout),
            sg.Tab("Tasks", tasksLayout),
            sg.Tab("Export", exportLayout),
                    ]])],
        ]

    # Create the Window
    mainWindow = sg.Window("DeviatorZ Account Checker", layout, font=("Helvetica", 15), finalize=True)
    mainWindow["log"].update(disabled=True)

    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="log.txt",
        filemode="a"
    )
    handler = Handler(mainWindow)
    logger = logging.getLogger("")
    logger.addHandler(handler)

    # Event Loop to process "events" and get the "values" of the inputs

    while True:
        event, values = mainWindow.read()
        if event == sg.WIN_CLOSED: # if user closes window
            break
        elif event == "start":
            mainWindow["start"].update(disabled=True)
            mainWindow["eraseExports"].update(disabled=True)
            Thread(target=execute, args=(copy.deepcopy(values), lock, mainWindow), daemon=True).start()
        elif event == "saveSettings":
            saveSettings(values)
        elif event == "saveTasks":
            saveTasks(values)
        elif event == "eraseExports":
            eraseFiles("export\\single")
            eraseFiles("export\\all")
            logger.info("Exports erased!")
        elif event == "openExports":
            try:
                os.startfile(f"{cwd}\\export")
            except:
                try:
                    subprocess.Popen(["xdg-open", f"{cwd}\\export"])
                except:
                    pass
        elif event == "saveExport":
            saveExport(values)
        elif "updateInformation":
            Thread(target=updateInformation, args=[mainWindow]).start()

    mainWindow.close()

if __name__ == "__main__":
    main()