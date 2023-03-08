from threading import Thread
from threading import Lock
from threading import Event
from clientMain.tasks import executeAllAccounts
from clientTasks.export import eraseFiles
from update import update
from TaskList import TaskList
import copy
import PySimpleGUI as sg
import logging
import os

# handles console logging
class Handler(logging.StreamHandler):
    def __init__(self, window):
        logging.StreamHandler.__init__(self)
        self.buffer = ""
        self.window = window

    def emit(self, record):
        self.format(record)
        record = f"{record.asctime} [{record.levelname}] {record.message}"
        self.buffer = f"{self.buffer}\n{record}".strip()
        try:
            self.window["log"].update(value=self.buffer)
        except: # GUI closed while running tasks
            pass

# launches tasks on accounts, reenables "start" and "erase exports" buttons once tasks are finished
def execute(values, lock, mainWindow, exitEvent):
    try:
        mainWindow["start"].update(disabled=True)
        mainWindow["eraseExports"].update(disabled=True)
    except: # GUI closed while running tasks
        return
    
    thread = Thread(target=executeAllAccounts, args=(values, lock, mainWindow["progress"], exitEvent))
    thread.start()
    thread.join()
    
    try:
        mainWindow["start"].update(disabled=False)
        mainWindow["eraseExports"].update(disabled=False)
    except: # GUI closed while running tasks
        pass

# launches skin and champion file update task
def updateInformation(mainWindow):
    mainWindow["updateInformation"].update(disabled=True)
    thread = Thread(target=update, args=[mainWindow])
    thread.start()
    thread.join()
    mainWindow["updateInformation"].update(disabled=False)

# saves options in settings tab
def saveSettings(values):
    sg.user_settings_set_entry("riotClient", values["riotClient"])
    sg.user_settings_set_entry("leagueClient", values["leagueClient"])
    sg.user_settings_set_entry("accountsFile", values["accountsFile"])
    sg.user_settings_set_entry("accountsDelimiter", values["accountsDelimiter"])
    sg.user_settings_set_entry("threadCount", values["threadCount"])

# saves options in tasks tab
def saveTasks(values):
    sg.user_settings_set_entry("claimEventRewards", values["claimEventRewards"])
    sg.user_settings_set_entry("buyChampionShardsWithTokens", values["buyChampionShardsWithTokens"])
    sg.user_settings_set_entry("buyBlueEssenceWithTokens", values["buyBlueEssenceWithTokens"])
    sg.user_settings_set_entry("craftKeys", values["craftKeys"])
    sg.user_settings_set_entry("openChests", values["openChests"])
    sg.user_settings_set_entry("openLoot", values["openLoot"])
    sg.user_settings_set_entry("disenchantChampionShards", values["disenchantChampionShards"])
    sg.user_settings_set_entry("disenchantEternalsShards", values["disenchantEternalsShards"])

# save options in export tab
def saveExport(values):
    sg.user_settings_set_entry("bannedTemplate", values["bannedTemplate"])
    sg.user_settings_set_entry("errorTemplate", values["errorTemplate"])
    sg.user_settings_set_entry("exportMin", values["exportMin"])

def getMainLayout():
    return [
        [sg.Output(size=(110, 25), key="log", font=("Helvetica", 8))],
        [sg.Button("Start", key="start"), sg.Button("Stop", key="stop"), sg.Button("Exports folder", key="openExports"), sg.Button("Erase exports", key="eraseExports"), sg.Text("", key="progress")] 
    ]  

def getSettingsLayout(cwd):
    return [
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

def getTasksLayout():
    tasks = TaskList.getTaskDisplay()

    return [
        [sg.Column([[sg.Text(taskGroupName, size=(30,1), font=("Helvetica", 8))]], pad=(0, None), expand_x=True) for taskGroupName in tasks],
        [sg.Column([[sg.Checkbox(task["text"], default=sg.user_settings_get_entry(taskName, True), key=taskName, size=(30,1), font=("Helvetica", 8))] for taskName, task in taskGroup.items()], pad=(0, None), expand_x=True, expand_y=True) for taskGroupName, taskGroup in tasks.items()],
        [sg.Button("Save", key="saveTasks")],
    ]

def getExportLayout():
    return [
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

def setupConsoleLogging(mainWindow):
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="log.txt",
        filemode="a"
    )
    handler = Handler(mainWindow)
    logger = logging.getLogger("")
    logger.addHandler(handler)

# setups the gui, console logging and handles main loop
def main():
    lock = Lock()
    cwd = os.getcwd()
    sg.theme("Black")
    sg.user_settings_filename("settings.json", path=cwd)

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

    exitEvent = Event()
    #executionThread = Thread(target=execute, args=(copy.deepcopy(values), lock, mainWindow, exitEvent)).start()

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
        elif event == "eraseExports":
            eraseFiles("export\\single")
            eraseFiles("export\\all")
            logging.info("Exports erased!")
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

if __name__ == "__main__":
    main()