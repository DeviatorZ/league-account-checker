from data.TaskList import TaskList
import PySimpleGUI as sg
import config
from client.champions import Champions

def getMainLayout():
    return [
        [sg.Multiline(size=(110, 25), key="log", font=("Helvetica", 8), write_only=True, autoscroll=True)],
        [sg.Button("Start", key="start"), sg.Button("Stop", key="stop"), sg.Button("Exports folder", key="openExports"), sg.Text("", key="progress")] 
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
        [sg.Text("Thread count"), sg.Combo([x for x in range(1,17)], default_value=sg.user_settings_get_entry("threadCount", "2"), key="threadCount")],
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
        [sg.Checkbox("Export failed (banned/error) accounts separately", default=sg.user_settings_get_entry("failedSeparately", False), key="failedSeparately", size=(70,1), font=("Helvetica", 9))],
        [sg.Text("Raw export type"), sg.Radio("Minimal", "export", default=sg.user_settings_get_entry("exportMin", False), key="exportMin"), 
            sg.Radio("Full", "export", default=not sg.user_settings_get_entry("exportMin", False))],
        [sg.Button("Delete raw data", key="deleteRaw")],
        [sg.Checkbox("Automatically delete raw data at the start of the checking process", default=sg.user_settings_get_entry("autoDeleteRaw", False), key="autoDeleteRaw", size=(70,1), font=("Helvetica", 9))],
        [sg.Button("Export now", key="exportNow")],
        [sg.Checkbox("Automatically export raw data at the end of the checking process", default=sg.user_settings_get_entry("autoExport", True), key="autoExport", size=(70,1), font=("Helvetica", 9))],
        [sg.Button("Save", key="saveExport"), sg.Push(), sg.Button("Update data", key="updateInformation")],
    ]

def getRefundsLayout():
    return [
        [sg.Checkbox("Refund champions (FREE)", default=sg.user_settings_get_entry("freeChampionRefunds", False), key="freeChampionRefunds", size=(30,2)),
         sg.Text("Minimum price"), sg.InputCombo((450, 1350, 3150, 4800, 6300), default_value=sg.user_settings_get_entry("freeChampionRefundsMinPrice", 1350), key="freeChampionRefundsMinPrice")],
        [sg.Checkbox("Refund champions (TOKENS)", default=sg.user_settings_get_entry("tokenChampionRefunds", False), key="tokenChampionRefunds", size=(30,1)),
         sg.Text("Minimum price"), sg.InputCombo((450, 1350, 3150, 4800, 6300), default_value=sg.user_settings_get_entry("tokenChampionRefundsMinPrice", 4800), key="tokenChampionRefundsMinPrice")],
        [sg.Button("Save", key="saveRefunds")],
    ]

def getChampionShopLayout():
    Champions.refreshData(config.CHAMPION_FILE_PATH)
    return [
        [sg.Checkbox("Buy Champions", default=sg.user_settings_get_entry("buyChampions", False), key="buyChampions", size=(30,1))],
        [sg.Multiline(sg.user_settings_get_entry("championShopList", ["Amumu", "Annie", "Ashe", "Brand", "Caitlyn", "Darius", "Diana", "Dr. Mundo", "Garen", "Leona", "Lux", "Malphite", "Master Yi", "Miss Fortune", "Nunu & Willump", "Poppy", "Sejuani", "Sivir", "Sona", "Soraka", "Teemo", "Warwick", "Yuumi"]), key="championShopList", size=(60,8))],
        [sg.InputCombo(sorted(Champions.getAllChampions()), default_value="Annie", key="championChoice", size=20), sg.Button("Add", key="addChampion"), sg.Button("Remove", key="removeChampion"), sg.Text("", key="championShopResponse", font=("Helvetica", 9))],
        [sg.Text("Maximum owned champions"), sg.Input(sg.user_settings_get_entry("maxOwnedChampions", 20), key="maxOwnedChampions", size=3)],
        [sg.Button("Save", key="saveChampionShop")],
    ]