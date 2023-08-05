from GUI.exceptions import InvalidPathException, InvalidInputException
import GUI.keys as guiKeys
import os
import csv
from typing import Dict, Any, List
from client.champions import Champions

def checkForFileErrors(settings: Dict[str, Any]) -> None:
    """
    Checks if the required files specified in the settings exist.

    :param settings: The dictionary of settings.

    Raises: 
        InvalidPathException: If any of the required files do not exist.
    """
    if not os.path.exists(settings[guiKeys.RIOT_CLIENT]):
        raise InvalidPathException("RiotClientServices.exe path doesn't exist!")

    if not os.path.exists(settings[guiKeys.LEAGUE_CLIENT]):
        raise InvalidPathException("LeagueClient.exe path doesn't exist!")

    if not os.path.exists(settings[guiKeys.ACCOUNT_FILE_PATH]):
        raise InvalidPathException("Account file path doesn't exist!")


def getAccounts(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Creates a list of accounts from an account file.

    :param settings: The dictionary of settings.

    Raises: 
        SyntaxError: If there is a syntax error in the account file.

    :return: The list of accounts.
    """
    accounts = []

    # read account file
    with open(settings[guiKeys.ACCOUNT_FILE_PATH], encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=settings[guiKeys.ACCOUNT_FILE_DELIMITER])
        for index, row in enumerate(reader, start=1):
            if row[0] == "":
                raise SyntaxError("Missing username in account file - Line " + str(index))
            elif row[1] == "":
                raise SyntaxError("Missing password in account file - Line " + str(index))
            accounts.append({
                "username" : row[0],
                "password" : row[1],
            })
    
    return accounts


def validateChampionShop(settings: Dict[str, Any]) -> None:
    try:
        settings[guiKeys.CHAMPION_SHOP_PURCHASE_LIST] = eval(settings[guiKeys.CHAMPION_SHOP_PURCHASE_LIST])
        if not type(settings[guiKeys.CHAMPION_SHOP_PURCHASE_LIST]) is list:
            raise Exception
    except Exception:
        raise InvalidInputException("Invalid champion shop list!")
    
    for championName in settings[guiKeys.CHAMPION_SHOP_PURCHASE_LIST]:
        championId = Champions.getChampionIdByName(championName)
        if championId is None:
            raise InvalidInputException(f"Invalid champion in champion shop list: {championName}")
        
    try:
        settings[guiKeys.MAXIMUM_OWNED_CHAMPIONS] = int(settings[guiKeys.MAXIMUM_OWNED_CHAMPIONS])
    except:
        raise InvalidInputException("Maximum owned champion count should be an integer!")   
