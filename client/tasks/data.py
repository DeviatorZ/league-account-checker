import json
from time import sleep
from client.champions import Champions
from client.skins import Skins
from client.connection.LeagueConnection import LeagueConnection
from typing import Dict, List, Any
from client.loot import Loot
import logging

def getSummoner(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's in-game name and level (adds the data to account data dictionary)

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param account: A dictionary containing account information.
    """
    summoner = leagueConnection.get("/lol-summoner/v1/current-summoner")
    summoner = summoner.json()

    account["summonerLevel"] = summoner["summonerLevel"]
    account["ign"] = summoner["displayName"]

def getHonorLevel(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's honor level (adds the data to account data dictionary)

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param account: A dictionary containing account information.
    """
    honor = leagueConnection.get("/lol-honor-v2/v1/profile").json()
    account["honorLevel"] = honor["honorLevel"]

def getEmailVerification(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's email is verification status (adds the data to account data dictionary)

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param account: A dictionary containing account information.
    """
    email = leagueConnection.get("/lol-email-verification/v1/email")
    email = email.json()

    if email["emailVerified"]:
        account["emailVerified"] = "Verified"
    else:
        account["emailVerified"] = "Unverified"

def getCurrencies(lootJsons: List[Dict[str, Any]], account: Dict[str, Any]) -> None:
    """
    Obtains the account's information on blue essence, orange essence, and riot points (adds the data to account data dictionary)

    :param lootJsons: A list of loot data.
    :param account: A dictionary containing account information.
    """
    account["be"] = 0
    account["oe"] = 0
    account["rp"] = 0

    for loot in lootJsons:
        if loot["lootId"] == "CURRENCY_champion":
            account["be"] = loot["count"]
        elif loot["lootId"] == "CURRENCY_cosmetic":
            account["oe"] = loot["count"]
        elif loot["lootId"] == "CURRENCY_RP":
            account["rp"] = loot["count"]

def getSkins(leagueConnection: LeagueConnection, loot: Loot, account: Dict[str, Any]) -> None:
    """
    Obtains the account's information on rental, permanent, and owned skins (adds the data to account data dictionary)

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    :param account: A dictionary containing account information.
    """
    skinShardsRental = loot.getShardIdsByPattern("CHAMPION_SKIN_RENTAL_(\d+)")
    account["skinShardsRental"] = ", ".join(Skins.getSkinById(id) for id in skinShardsRental if Skins.getSkinById(id) is not None)
    account["skinShardsRentalCount"] = len(skinShardsRental)

    skinShardsPermanent = loot.getShardIdsByPattern("CHAMPION_SKIN_(\d+)")
    account["skinShardsPermanent"] = ", ".join(Skins.getSkinById(id) for id in skinShardsPermanent if Skins.getSkinById(id) is not None)
    account["skinShardsPermanentCount"] = len(skinShardsPermanent)

    ownedSkins = leagueConnection.get("/lol-inventory/v2/inventory/CHAMPION_SKIN").json()
    account["ownedSkins"] = ", ".join(Skins.getSkinById(skin["itemId"]) for skin in ownedSkins if Skins.getSkinById(skin["itemId"]) is not None and skin["ownershipType"] == "OWNED")
    # some skins in ownedSkins json might be rented so count owned skins manually
    seperatorCount = account["ownedSkins"].count(", ") 
    if seperatorCount > 0:
        account["ownedSkinsCount"] = seperatorCount + 1
    elif account["ownedSkins"]:
        account["ownedSkinsCount"] = 1
    else:
        account["ownedSkinsCount"] = 0
    
    account["skinShardsAll"] = ', '.join(filter(None, (account["skinShardsRental"], account["skinShardsPermanent"])))
    account["skinShardsAllCount"] = account["skinShardsRentalCount"] + account["skinShardsPermanentCount"]

    account["allSkins"] = ', '.join(filter(None, (account["skinShardsAll"], account["ownedSkins"])))
    account["allSkinsCount"] = account["skinShardsAllCount"] + account["ownedSkinsCount"]

# obtains account's information on owned champions
def getChampions(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's information on owned champions (adds the data to account data dictionary)

    :param leagueConnection: The session object for making API requests.
    :param account: A dictionary containing account information.
    """
    ownedChampions = leagueConnection.get("/lol-champions/v1/owned-champions-minimal").json()
    account["ownedChampions"] = ", ".join(Champions.getChampionById(champion["id"]) for champion in ownedChampions if Champions.getChampionById(champion["id"]) is not None and champion["ownership"]["owned"])
    # owned champions endpoint includes free rotation champions so count owned champions manually
    seperatorCount = account["ownedChampions"].count(", ")
    if seperatorCount > 0:
        account["ownedChampionsCount"] = seperatorCount + 1
    elif account["ownedChampions"]:
        account["ownedChampionsCount"] = 1
    else:
        account["ownedChampionsCount"] = 0

def getRank(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's ranked stats on soloq and flexq modes (adds the data to account data dictionary)

    :param leagueConnection: The session object for making API requests.
    :param account: A dictionary containing account information.
    """
    romanNumbers = {
        "IV": 4,
        "III": 3,
        "II": 2,
        "I": 1,
    }   

    rankedStats = leagueConnection.get("/lol-ranked/v1/current-ranked-stats").json()

    soloTier = ((rankedStats["queueMap"]["RANKED_SOLO_5x5"]["tier"]).lower()).capitalize()
    if not soloTier:
        account["soloTier"] = "Unranked"
        account["soloTierStart"] = "U"
        account["soloDivision"] = ""
        account["soloDivisionDigit"] = ""
        account["soloLP"] = ""
        account["soloWins"] = ""
        account["soloLosses"] = ""
        account["soloWinrate"] = ""
    else:
        account["soloTier"] = soloTier
        account["soloTierStart"] = soloTier[0]
        account["soloDivision"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["division"]
        account["soloDivisionDigit"] = romanNumbers[account["soloDivision"]]
        account["soloLP"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["leaguePoints"]
        account["soloWins"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["wins"]
        account["soloLosses"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["losses"]
        account["soloWinrate"] = round(account["soloWins"] / (account["soloWins"] + account["soloLosses"]) * 100)

    flexTier = ((rankedStats["queueMap"]["RANKED_FLEX_SR"]["tier"]).lower()).capitalize()
    if not flexTier:
        account["flexTier"] = "Unranked"
        account["flexTierStart"] = "U"
        account["flexDivision"] = ""
        account["flexDivisionDigit"] = ""
        account["flexLP"] = ""
        account["flexWins"] = ""
        account["flexLosses"] = ""
        account["flexWinrate"] = ""
    else:
        account["flexTier"] = flexTier
        account["flexTierStart"] = flexTier[0]
        account["flexDivision"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["division"]
        account["flexDivisionDigit"] = romanNumbers[account["flexDivision"]]
        account["flexLP"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["leaguePoints"]
        account["flexWins"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["wins"]
        account["flexLosses"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["losses"]
        account["flexWinrate"] = round(account["flexWins"] / (account["flexWins"] + account["flexLosses"]) * 100)

def getLowPriorityQueue(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Tries to queue up and checks if there's a low priority queue penalty (adds the data to account data dictionary)
    

    :param leagueConnection: The session object for making API requests.
    :param account: The account object to store the retrieved data.
    """
    leagueConnection.waitForUpdate()
    
    queueArgs = {
        "queueId": 430, # Blind pick
    }
    queueArgs = json.dumps(queueArgs, indent = 4)
    
    leagueConnection.post("/lol-lobby/v2/lobby", queueArgs)
    sleep(1)

    leagueConnection.post("/lol-lobby/v2/lobby/matchmaking/search")
    sleep(1)

    queueState = leagueConnection.get("/lol-matchmaking/v1/search").json()

    account["lowPriorityQueue"] = "OtherPenalty"

    if queueState["lowPriorityData"]["reason"] == "LEAVER_BUSTED":
        account["lowPriorityQueue"] = str(int(queueState["lowPriorityData"]["penaltyTime"] / 60)) + " minutes"
    elif queueState["searchState"] == "Found" or queueState["searchState"] == "Searching": # searching for game or found one (no penalties)
        account["lowPriorityQueue"] = "None"

def getData(leagueConnection: LeagueConnection, account: Dict[str, Any], loot: Loot) -> None:
    """
    Uses all data functions to get information about the account.

    :param leagueConnection: The session object for making API requests.
    :param account: The account data dictionary for storing the retrieved data.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    lootJson = loot.getLoot()
    getCurrencies(lootJson, account)
    
    getHonorLevel(leagueConnection, account)
    getSummoner(leagueConnection, account)
    getEmailVerification(leagueConnection, account)

    getChampions(leagueConnection, account)

    getSkins(leagueConnection, loot, account)

    getRank(leagueConnection, account)
    getLowPriorityQueue(leagueConnection, account)