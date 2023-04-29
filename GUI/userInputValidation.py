from GUI.exceptions import InvalidPathException
import os
import csv

# make sure user input files exist
def checkForFileErrors(settings):
    if not os.path.exists(settings["riotClient"]):
        raise InvalidPathException("RiotClientServices.exe path doesn't exist!")

    if not os.path.exists(settings["leagueClient"]):
        raise InvalidPathException("LeagueClient.exe path doesn't exist!")

    if not os.path.exists(settings["accountsFile"]):
        raise InvalidPathException("Account file path doesn't exist!")

# creates account list from a file
def getAccounts(settings):
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