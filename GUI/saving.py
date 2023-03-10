import PySimpleGUI as sg

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