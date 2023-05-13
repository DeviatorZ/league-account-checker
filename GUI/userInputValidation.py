from GUI.exceptions import InvalidPathException
import os
import csv
from typing import Dict, Any, List

def checkForFileErrors(settings: Dict[str, Any]) -> None:
    """
    Checks if the required files specified in the settings exist.

    :param settings: The dictionary of settings.

    Raises: 
        InvalidPathException: If any of the required files do not exist.
    """
    if not os.path.exists(settings["riotClient"]):
        raise InvalidPathException("RiotClientServices.exe path doesn't exist!")

    if not os.path.exists(settings["leagueClient"]):
        raise InvalidPathException("LeagueClient.exe path doesn't exist!")

    if not os.path.exists(settings["accountsFile"]):
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
    with open(settings["accountsFile"], encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=settings["accountsDelimiter"])
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