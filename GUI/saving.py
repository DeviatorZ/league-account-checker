import PySimpleGUI as sg
from typing import List, Dict, Any

def save(values: Dict[str, Any], keyList: List[str]) -> None:
    """
    Saves the specified keys to user setting file.

    :param values: The dictionary of values.
    :param keyList: The list of keys to save.
    """
    for key in keyList:
        sg.user_settings_set_entry(key, values[key])


def saveSettings(values: Dict[str, Any]) -> None:
    """
    Saves options from the Settings tab.

    :param values: The dictionary of values.
    """
    allSettings = [
        "riotClient", 
        "leagueClient",
        "accountsFile",
        "accountsDelimiter",
        "threadCount"
    ]
    save(values, allSettings)

def saveTasks(values: Dict[str, Any]) -> None:
    """
    Saves options from the Tasks tab.

    :param values: The dictionary of values.
    """
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

def saveExport(values: Dict[str, Any]) -> None:
    """
    Saves options from the Export tab.

    :param values: The dictionary of values.
    """
    allExports = [
        "bannedTemplate",
        "errorTemplate",
        "failedSeparately",
        "exportMin",
        "autoDeleteRaw",
        "autoExport",
    ]

    save(values, allExports)

def saveRefunds(values: Dict[str, Any]) -> None:
    """
    Saves options from the Refunds tab.

    :param values: The dictionary of values.
    """
    allRefunds = [
        "freeChampionRefunds",
        "freeChampionRefundsMinPrice",
        "tokenChampionRefunds",
        "tokenChampionRefundsMinPrice",
    ]

    save(values, allRefunds)