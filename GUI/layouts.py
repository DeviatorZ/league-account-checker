from data.TaskList import TaskList
import PySimpleGUI as sg
import config
from client.champions import Champions
import GUI.keys as guiKeys

def getMainLayout():
    return [
        [sg.Multiline(size=(110, 35), key="log", font=("Helvetica", 8), write_only=True, autoscroll=True)],
        [sg.VPush()],
        [sg.Button("Start", key="start"), sg.Button("Stop", key="stop"), sg.Button("Export Folder", key="openExports"), sg.Text("", key="progress")] 
    ]  

def getSettingsLayout(cwd):
    return [
        [sg.Text("RiotClientServices.exe Location")],
        [sg.Input(sg.user_settings_get_entry(guiKeys.RIOT_CLIENT, "C:\\Riot Games\\Riot Client\\RiotClientServices.exe"), key=guiKeys.RIOT_CLIENT), sg.FileBrowse()],
        [sg.Text("LeagueClient.exe Location")],
        [sg.Input(sg.user_settings_get_entry(guiKeys.LEAGUE_CLIENT, "C:\\Riot Games\\League of Legends\\LeagueClient.exe"), key=guiKeys.LEAGUE_CLIENT), sg.FileBrowse()],
        [sg.Text("Account File Location")],
        [sg.Input(sg.user_settings_get_entry(guiKeys.ACCOUNT_FILE_PATH, cwd + "\\accounts.csv"), key=guiKeys.ACCOUNT_FILE_PATH), sg.FileBrowse()],
        [sg.Text("Account File Delimiter"), sg.InputCombo((",",":",";"), default_value=sg.user_settings_get_entry(guiKeys.ACCOUNT_FILE_DELIMITER, ":"), key=guiKeys.ACCOUNT_FILE_DELIMITER)],
        [sg.Text("Thread Count"), sg.Combo([x for x in range(1,17)], default_value=sg.user_settings_get_entry("threadCount", 2), key="threadCount")],
        [sg.VPush()],
        [sg.Button("Save", key="saveSettings")],
    ]

def getTasksLayout():
    tasks = TaskList.getTaskDisplay()

    return [
        [sg.Column([[sg.Text(taskGroupName, size=(30,1), font=("Helvetica", 8))]], pad=(0, None), expand_x=True) for taskGroupName in tasks],
        [sg.Column([[sg.Checkbox(task["text"], default=sg.user_settings_get_entry(taskName, True), key=taskName, size=(30,1), font=("Helvetica", 8))] for taskName, task in taskGroup.items()], pad=((0, 0), (0, 10)), expand_x=True, expand_y=False) for taskGroupName, taskGroup in tasks.items()],
        [sg.Text("Refunding", font=("Helvetica", 8))],
        [sg.Checkbox("Refund Champions (FREE)", default=sg.user_settings_get_entry(guiKeys.USE_FREE_CHAMPION_REFUNDS, False), key=guiKeys.USE_FREE_CHAMPION_REFUNDS, size=(30,2), font=("Helvetica", 8)),
         sg.Text("Minimum Price (BE)", font=("Helvetica", 8)), sg.InputCombo((450, 1350, 3150, 4800, 6300), default_value=sg.user_settings_get_entry(guiKeys.USE_FREE_CHAMPION_REFUNDS_MIN_PRICE_BE, 1350), key=guiKeys.USE_FREE_CHAMPION_REFUNDS_MIN_PRICE_BE, font=("Helvetica", 8))],
        [sg.Checkbox("Refund Champions (TOKENS)", default=sg.user_settings_get_entry(guiKeys.USE_TOKEN_CHAMPION_REFUNDS, False), key=guiKeys.USE_TOKEN_CHAMPION_REFUNDS, size=(30,2), font=("Helvetica", 8)),
         sg.Text("Minimum Price (BE)", font=("Helvetica", 8)), sg.InputCombo((450, 1350, 3150, 4800, 6300), default_value=sg.user_settings_get_entry(guiKeys.USE_TOKEN_CHAMPION_REFUNDS_MIN_PRICE_BE, 4800), key=guiKeys.USE_TOKEN_CHAMPION_REFUNDS_MIN_PRICE_BE, font=("Helvetica", 8))],
        [sg.VPush()],
        [sg.Button("Save", key="saveTasks")],
    ]

def getDatatLayout():
    return [
        [sg.Text("At The Start Of The Checking Process:")],
        [sg.Checkbox("Delete Old Data", default=sg.user_settings_get_entry(guiKeys.DELETE_RAW, False), key=guiKeys.DELETE_RAW, size=(70,1), font=("Helvetica", 9))], 

        [sg.Text("During The Checking Process:")], 
        [sg.Checkbox("Skip Running An Account If Data Is Already Available:", default=sg.user_settings_get_entry(guiKeys.SKIP_ACCOUNTS_WITH_DATA, False), key=guiKeys.SKIP_ACCOUNTS_WITH_DATA, size=(70,1), font=("Helvetica", 9))],
        [sg.Text("Don't Skip If Data Is Older Than:", size=(70,1), font=("Helvetica", 9), pad=(40,0))],
        [sg.Radio("A Day", "skipAccountTimeOptions", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_DAY_OLD, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_DAY_OLD, size=(10,1), font=("Helvetica", 9), pad=((80,0), (0,0))),
            sg.Radio("A Week", "skipAccountTimeOptions", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_WEEK_OLD, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_WEEK_OLD, size=(10,1), font=("Helvetica", 9)),
            sg.Radio("Skip All", "skipAccountTimeOptions", default=sg.user_settings_get_entry(guiKeys.SKIP_ACCOUNTS_WITH_INDEFINITE_DATA_AGE, True), key=guiKeys.SKIP_ACCOUNTS_WITH_INDEFINITE_DATA_AGE, size=(10,1), font=("Helvetica", 9))],
        [sg.Text("Don't Skip If Account State In Data Is:", size=(70,1), font=("Helvetica", 9), pad=(40,0))],
        [sg.Checkbox("Permanently Banned", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_PERMABANNED, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_PERMABANNED, size=(70,1), font=("Helvetica", 9), pad=(80,0))],
        [sg.Checkbox("Temporarily Banned", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_BANNED, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_BANNED, size=(70,1), font=("Helvetica", 9), pad=(80,0))],
        [sg.Checkbox("AUTH_FAILURE (Invalid Credentials)", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_AUTH_FAILURE, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_AUTH_FAILURE, size=(70,1), font=("Helvetica", 9), pad=(80,0))],
        [sg.Checkbox("RETRY_LIMIT_EXCEEDED (Too many failed attempts)", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_TOO_MANY_ATTEMPS, True), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_TOO_MANY_ATTEMPS, size=(70,1), font=("Helvetica", 9), pad=(80,0))],
        [sg.Checkbox("Other Errors", default=sg.user_settings_get_entry(guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_GENERAL_ERROR, False), key=guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_GENERAL_ERROR, size=(70,1), font=("Helvetica", 9), pad=(80,0))],

        [sg.Text("Data Obtained During The Checking Process:"), sg.Radio("MINIMAL", "export", default=sg.user_settings_get_entry(guiKeys.EXPORT_MINIMAL, False), key=guiKeys.EXPORT_MINIMAL), 
            sg.Radio("FULL", "export", default=not sg.user_settings_get_entry(guiKeys.EXPORT_MINIMAL, False))],

        [sg.Text("At The End Of The Checking Process:")], 
        [sg.Radio("Export Only Input File Account Data", "postrunDataTasks", default=sg.user_settings_get_entry(guiKeys.AUTO_EXPORT_INPUT_ONLY, True), key=guiKeys.AUTO_EXPORT_INPUT_ONLY, size=(70,1), font=("Helvetica", 9))],
        [sg.Radio("Export All Data", "postrunDataTasks", default=sg.user_settings_get_entry(guiKeys.AUTO_EXPORT, False), key=guiKeys.AUTO_EXPORT, size=(70,1), font=("Helvetica", 9))],
        [sg.Radio("Do Nothing", "postrunDataTasks", default=sg.user_settings_get_entry(guiKeys.DONT_AUTO_EXPORT, False), key=guiKeys.DONT_AUTO_EXPORT, size=(70,1), font=("Helvetica", 9))],

        [sg.Button("Delete Data", key="deleteRaw")],
        [sg.VPush()],
        [sg.Button("Save", key="saveDataTab"), sg.Push(), sg.Button("Update Local Champion/Skin/Loot Information", key="updateInformation")],
    ]

def getExportLayout():
    return [
        [sg.Text("Banned State Account Export Template")],
        [sg.Input(sg.user_settings_get_entry(guiKeys.BANNED_ACCOUNT_STATE_TEMPLATE, "{username};{password};{region};{banReason} {banExpiration}"), key=guiKeys.BANNED_ACCOUNT_STATE_TEMPLATE, size=60)],
        [sg.Text("Error State Account Export Template")],
        [sg.Input(sg.user_settings_get_entry(guiKeys.ERROR_ACCOUNT_STATE_TEMPLATE, "{username};{password};{state}"), key=guiKeys.ERROR_ACCOUNT_STATE_TEMPLATE, size=60)],
        [sg.Checkbox("Export Failed State(Banned/Error) Accounts Separately", default=sg.user_settings_get_entry(guiKeys.EXPORT_FAILED_SEPARATELY, False), key=guiKeys.EXPORT_FAILED_SEPARATELY, size=(70,1), font=("Helvetica", 9))],
        [sg.Button("Export All Data", key="exportNow")],
        [sg.Button("Export Only Input File Account Data", key="exportNowOnlyInput")],
        [sg.VPush()],
        [sg.Button("Save", key="saveExport")],
    ]

def getChampionShopLayout():
    Champions.refreshData(config.CHAMPION_FILE_PATH)
    return [
        [sg.Checkbox("Buy Champions", default=sg.user_settings_get_entry(guiKeys.BUY_CHAMPIONS, False), key=guiKeys.BUY_CHAMPIONS, size=(30,1))],
        [sg.Multiline(sg.user_settings_get_entry(guiKeys.CHAMPION_SHOP_PURCHASE_LIST, ["Amumu", "Annie", "Ashe", "Brand", "Caitlyn", "Darius", "Diana", "Dr. Mundo", "Garen", "Leona", "Lux", "Malphite", "Master Yi", "Miss Fortune", "Nunu & Willump", "Poppy", "Sejuani", "Sivir", "Sona", "Soraka", "Teemo", "Warwick", "Yuumi"]), key=guiKeys.CHAMPION_SHOP_PURCHASE_LIST, size=(60,8))],
        [sg.InputCombo(sorted(Champions.getAllChampions()), default_value="Annie", key="championChoice", size=20), sg.Button("Add", key="addChampion"), sg.Button("Remove", key="removeChampion"), sg.Text("", key="championShopResponse", font=("Helvetica", 9))],
        [sg.Text("Maximum Owned Champions"), sg.Input(sg.user_settings_get_entry(guiKeys.MAXIMUM_OWNED_CHAMPIONS, 20), key=guiKeys.MAXIMUM_OWNED_CHAMPIONS, size=3)],
        [sg.VPush()],
        [sg.Button("Save", key="saveChampionShop")],
    ]