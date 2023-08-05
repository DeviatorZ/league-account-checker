import json
from time import sleep
from client.champions import Champions
from client.skins import Skins
from client.lootdata import LootData
from client.connection.LeagueConnection import LeagueConnection
from typing import Dict, List, Any
from client.loot import Loot
from datetime import datetime
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
    account["email"] = email["email"]

    if email["emailVerified"]:
        account["emailVerified"] = "Verified"
    else:
        account["emailVerified"] = "Unverified"

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

    allOwnedSkins = leagueConnection.get("/lol-inventory/v2/inventory/CHAMPION_SKIN").json()
    ownedChromas = []
    ownedSkins = []

    for skin in allOwnedSkins:
        if not skin["ownershipType"] == "OWNED":
            continue

        id = skin["itemId"]
        name = Skins.getSkinById(id)
        if name:
            ownedSkins.append(name)
        elif Skins.isChroma(id):
            shopInfo = leagueConnection.get(f"/lol-purchase-widget/v1/purchasable-item?inventoryType=CHAMPION_SKIN&itemId={id}").json()
            name = shopInfo["item"]["name"]
            ownedChromas.append(name)
        else:
            logging.error(f"Couldn't obtain skin name - ID={id}. Is the skin data up to date?")
            ownedSkins.append(f"ID={id}")

    account["ownedSkins"] = ", ".join(ownedSkins)
    account["ownedSkinsCount"] = len(ownedSkins)

    account["skinShardsAll"] = ', '.join(filter(None, (account["skinShardsRental"], account["skinShardsPermanent"])))
    account["skinShardsAllCount"] = account["skinShardsRentalCount"] + account["skinShardsPermanentCount"]

    account["allSkins"] = ', '.join(filter(None, (account["skinShardsAll"], account["ownedSkins"])))
    account["allSkinsCount"] = account["skinShardsAllCount"] + account["ownedSkinsCount"]

    account["ownedSkinChromas"] = ", ".join(ownedChromas)
    account["ownedSkinChromasCount"] = len(ownedChromas)

# obtains account's information on owned champions
def getChampions(leagueConnection: LeagueConnection, account: Dict[str, Any]) -> None:
    """
    Obtains the account's information on owned champions (adds the data to account data dictionary)

    :param leagueConnection: The session object for making API requests.
    :param account: A dictionary containing account information.
    """
    ownedChampions = leagueConnection.get("/lol-champions/v1/owned-champions-minimal").json()
    ownedChampionList = []
    for champion in ownedChampions:
        id = champion["id"]
        name = Champions.getChampionById(id)
        if not name:
            logging.error(f"Couldn't obtain champion name - ID={id}. Is the champion data up to date?")
            name = f"ID={id}"
        ownedChampionList.append(name)

    account["ownedChampions"] = ", ".join(ownedChampionList)
    account["ownedChampionsCount"] = len(ownedChampionList)

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
    if not soloTier or soloTier == "None":
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
        account["soloDivision"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"].get("division", "")
        account["soloDivisionDigit"] = romanNumbers.get(account["soloDivision"], "")
        account["soloLP"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["leaguePoints"]
        account["soloWins"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["wins"]
        account["soloLosses"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["losses"]
        account["soloWinrate"] = round(account["soloWins"] / (account["soloWins"] + account["soloLosses"]) * 100)

    previousSoloTier = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["previousSeasonEndTier"]
    if previousSoloTier:
        account["previousSeasonSoloTier"] = previousSoloTier.lower().capitalize()
        account["previousSeasonSoloDivision"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"].get("previousSeasonEndDivision", "")
        account["previousSeasonSoloDivisionDigit"] = romanNumbers.get(account["previousSeasonSoloDivision"], "")
    else:
        account["previousSeasonSoloTier"] = ""
        account["previousSeasonSoloDivision"] = ""
        account["previousSeasonSoloDivisionDigit"] = ""

    flexTier = ((rankedStats["queueMap"]["RANKED_FLEX_SR"]["tier"]).lower()).capitalize()
    if not flexTier or flexTier == "None":
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
        account["flexDivision"] = rankedStats["queueMap"]["RANKED_FLEX_SR"].get("division", "")
        account["flexDivisionDigit"] = romanNumbers.get(account["flexDivision"], "")
        account["flexLP"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["leaguePoints"]
        account["flexWins"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["wins"]
        account["flexLosses"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["losses"]
        account["flexWinrate"] = round(account["flexWins"] / (account["flexWins"] + account["flexLosses"]) * 100)

    previousFlexTier = rankedStats["queueMap"]["RANKED_FLEX_SR"]["previousSeasonEndTier"]
    if previousFlexTier:
        account["previousSeasonFlexTier"] = previousFlexTier.lower().capitalize()
        account["previousSeasonFlexDivision"] = rankedStats["queueMap"]["RANKED_FLEX_SR"].get("previousSeasonEndDivision", "")
        account["previousSeasonFlexDivisionDigit"] = romanNumbers.get(account["previousSeasonFlexDivision"], "")
    else:
        account["previousSeasonFlexTier"] = ""
        account["previousSeasonFlexDivision"] = ""
        account["previousSeasonFlexDivisionDigit"] = ""

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
    sleep(2)

    leagueConnection.post("/lol-lobby/v2/lobby/matchmaking/search")
    sleep(2)

    queueState = leagueConnection.get("/lol-matchmaking/v1/search").json()

    account["lowPriorityQueue"] = "OtherPenalty"

    if queueState["lowPriorityData"]["reason"] == "LEAVER_BUSTED":
        account["lowPriorityQueue"] = str(int(queueState["lowPriorityData"]["penaltyTime"] / 60)) + " minutes"
    elif queueState["searchState"] == "Found" or queueState["searchState"] == "Searching": # searching for game or found one (no penalties)
        account["lowPriorityQueue"] = "None"

def getLastMatch(leagueConnection, account):
    matchHistory = leagueConnection.get("/lol-match-history/v1/products/lol/current-summoner/matches").json()["games"]["games"]
    if len(matchHistory) == 0:
        lastMatchData = "None"
    else:
        timestamp = matchHistory[0]["gameCreation"]
        lastMatchData = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %Hh%Mm%Ss')

    account["lastMatch"] = lastMatchData

def getLoot(lootJson: Dict[str, Any], account: List[Dict[str, Any]]) -> None:
    otherLoot = []
    skipLootList = ("CHAMPION_SKIN", "CHAMPION", "CURRENCY_champion", "CURRENCY_cosmetic", "CURRENCY_RP", "WARD_SKIN")
    account["be"] = 0
    account["oe"] = 0
    account["rp"] = 0

    for loot in lootJson:
        id = loot["lootId"]
        count = loot["count"]
        if id == "CURRENCY_champion":
            account["be"] = loot["count"]
        elif id == "CURRENCY_cosmetic":
            account["oe"] = loot["count"]
        elif id == "CURRENCY_RP":
            account["rp"] = loot["count"]
        elif id == "CURRENCY_mythic":
            otherLoot.append(f"{count}x Mythic Essence")
        elif id == "MATERIAL_key_fragment":
            otherLoot.append(f"{count}x Key Fragments")
        elif id.startswith(skipLootList) or id == "":
            continue
        else:
            name = LootData.getLootById(loot["lootId"])
            if not name:
                logging.error(f"Couldn't obtain loot name - ID={id}. Is the loot data up to date?")
                name = f"ID={id}"

            otherLoot.append(f"{count}x {name}")
    
    account["otherLoot"] = ", ".join(otherLoot)

def getData(leagueConnection: LeagueConnection, account: Dict[str, Any], loot: Loot) -> None:
    """
    Uses all data functions to get information about the account.

    :param leagueConnection: The session object for making API requests.
    :param account: The account data dictionary for storing the retrieved data.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    lootJson = loot.getLoot()
    
    getHonorLevel(leagueConnection, account)
    getSummoner(leagueConnection, account)
    getEmailVerification(leagueConnection, account)

    getChampions(leagueConnection, account)
    getSkins(leagueConnection, loot, account)
    getLoot(lootJson, account)

    getRank(leagueConnection, account)
    getLowPriorityQueue(leagueConnection, account)
    getLastMatch(leagueConnection, account)