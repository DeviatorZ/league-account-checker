import PySimpleGUI as sg
def save(values, keyList):
    for key in keyList:
        sg.user_settings_set_entry(key, values[key])

# saves options in settings tab
def saveSettings(values):
    allSettings = [
        "riotClient", 
        "leagueClient",
        "accountsFile",
        "accountsDelimiter",
        "threadCount"
    ]
    save(values, allSettings)

# saves options in tasks tab
def saveTasks(values):
    allTasks = [
        "claimEventRewards",
        "buyChampionShardsWithTokens",
        "buyBlueEssenceWithTokens",
        "craftKeys",
        "openChests",
        "openLoot",
        "disenchantChampionShards",
        "disenchantEternalsShards",
    ]

    save(values, allTasks)

# save options in export tab
def saveExport(values):
    allExports = [
        "bannedTemplate",
        "errorTemplate",
        "failedSeparately",
        "exportMin",
        "autoDeleteRaw",
        "autoExport",
    ]

    save(values, allExports)