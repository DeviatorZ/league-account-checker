import PySimpleGUI as sg
from typing import List, Dict, Any
import GUI.keys as guiKeys

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
        guiKeys.RIOT_CLIENT, 
        guiKeys.LEAGUE_CLIENT,
        guiKeys.ACCOUNT_FILE_PATH,
        guiKeys.ACCOUNT_FILE_DELIMITER,
        guiKeys.THREAD_COUNT,
        guiKeys.HEADLESS,
        guiKeys.SKIP_LOW_PRIO_CHECK,
    ]
    save(values, allSettings)

def saveTasks(values: Dict[str, Any]) -> None:
    """
    Saves options from the Tasks tab.

    :param values: The dictionary of values.
    """
    allTasks = [
        guiKeys.CLAIM_EVENT_REWARDS,
        guiKeys.BUY_CHAMPION_SHARDS_WITH_EVENT_TOKENS,
        guiKeys.BUY_BE_WITH_TOKENS,
        guiKeys.CRAFT_KEYS,
        guiKeys.OPEN_CHESTS,
        guiKeys.OPEN_LOOT,
        guiKeys.DISENCHANT_CHAMPION_SHARDS,
        guiKeys.DISENCHANT_ETERNALS_SHARDS,
        guiKeys.USE_FREE_CHAMPION_REFUNDS,
        guiKeys.USE_FREE_CHAMPION_REFUNDS_MIN_PRICE_BE,
        guiKeys.USE_TOKEN_CHAMPION_REFUNDS,
        guiKeys.USE_TOKEN_CHAMPION_REFUNDS_MIN_PRICE_BE,
    ]

    save(values, allTasks)

def saveData(values: Dict[str, Any]) -> None:
    """
    Saves options from the Data tab.

    :param values: The dictionary of values.
    """
    allData = [
        guiKeys.SKIP_ACCOUNTS_WITH_DATA,
        guiKeys.DELETE_RAW,
        guiKeys.EXPORT_MINIMAL,
        guiKeys.AUTO_EXPORT,
        guiKeys.AUTO_EXPORT_INPUT_ONLY,
        guiKeys.DONT_AUTO_EXPORT,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_DAY_OLD,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_DATA_ONE_WEEK_OLD,
        guiKeys.SKIP_ACCOUNTS_WITH_INDEFINITE_DATA_AGE,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_GENERAL_ERROR,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_BANNED,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_PERMABANNED,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_AUTH_FAILURE,
        guiKeys.DONT_SKIP_ACCOUNTS_WITH_STATE_TOO_MANY_ATTEMPS,
    ]

    save(values, allData)

def saveExport(values: Dict[str, Any]) -> None:
    """
    Saves options from the Export tab.

    :param values: The dictionary of values.
    """
    allExports = [
        guiKeys.BANNED_ACCOUNT_STATE_TEMPLATE,
        guiKeys.ERROR_ACCOUNT_STATE_TEMPLATE,
        guiKeys.EXPORT_FAILED_SEPARATELY,
    ]

    save(values, allExports)

def saveChampionShop(values: Dict[str, Any]) -> None:
    """
    Saves options from the Champion Shop tab.

    :param values: The dictionary of values.
    """
    allChampionShop = [
        guiKeys.BUY_CHAMPIONS,
        guiKeys.CHAMPION_SHOP_PURCHASE_LIST,
        guiKeys.MAXIMUM_OWNED_CHAMPIONS,
    ]

    save(values, allChampionShop)

def saveCaptcha(values: Dict[str, Any]) -> None:
    """
    Saves options from the Captcha tab.

    :param values: The dictionary of values.
    """
    allCaptcha = [
        guiKeys.CAPTCHA_SOLVER,
        guiKeys.CAPTCHA_API_KEY,
    ]

    save(values, allCaptcha)