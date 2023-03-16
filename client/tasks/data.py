import json
from time import sleep

# handles champion file for id to name conversion
class Champions():
    def __init__(self, path):
        with open(path, "r", encoding="utf8") as filePointer:
            self.championData = json.load(filePointer)

            self.championById = {}
            for champion in self.championData:
                self.championById[champion["id"]] = champion["name"]

    def getChampionById(self, id):
        try:
            return self.championById[id]
        except:
            return None

# handles skin file for id to name conversion
class Skins():
    def __init__(self, path):
        with open(path, "r", encoding="utf8") as filePointer:
            self.skinById = json.load(filePointer)

    def getSkinById(self, id):
        try:
            return self.skinById[str(id)]["name"]
        except:
            return None

# obtains account's in-game name and level
def getSummoner(leagueConnection, account):
    summoner = leagueConnection.get("/lol-summoner/v1/current-summoner")
    summoner = summoner.json()

    account["summonerLevel"] = summoner["summonerLevel"]
    account["ign"] = summoner["displayName"]

# obtains account's honor level
def getHonorLevel(leagueConnection, account):
    honor = leagueConnection.get("/lol-honor-v2/v1/profile").json()
    account["honorLevel"] = honor["honorLevel"]

# checks if account email is verified 
def getEmailVerification(leagueConnection, account):
    email = leagueConnection.get("/lol-email-verification/v1/email")
    email = email.json()

    if email["emailVerified"]:
        account["emailVerified"] = "Verified"
    else:
        account["emailVerified"] = "Unverified"

# obtains data on account's blue essence, orange essence and riot points
def getCurrencies(lootJson, account):
    account["be"] = 0
    account["oe"] = 0
    account["rp"] = 0

    for loot in lootJson:
        if loot["lootId"] == "CURRENCY_champion":
            account["be"] = loot["count"]
        elif loot["lootId"] == "CURRENCY_cosmetic":
            account["oe"] = loot["count"]
        elif loot["lootId"] == "CURRENCY_RP":
            account["rp"] = loot["count"]

# obtains account's information on rental, permanent and owned skins
def getSkins(leagueConnection, loot, skins, account):
    skinShardsRental = loot.getShardIdsByPattern("CHAMPION_SKIN_RENTAL_(\d+)")
    account["skinShardsRental"]= ", ".join(skins.getSkinById(id) for id in skinShardsRental if skins.getSkinById(id) is not None)
    account["skinShardsRentalCount"] = len(skinShardsRental)

    skinShardsPermanent = loot.getShardIdsByPattern("CHAMPION_SKIN_(\d+)")
    account["skinShardsPermanent"]= ", ".join(skins.getSkinById(id) for id in skinShardsPermanent if skins.getSkinById(id) is not None)
    account["skinShardsPermanentCount"] = len(skinShardsPermanent)

    ownedSkins = leagueConnection.get("/lol-inventory/v2/inventory/CHAMPION_SKIN").json()
    account["ownedSkins"] = ", ".join(skins.getSkinById(skin["itemId"]) for skin in ownedSkins if skins.getSkinById(skin["itemId"]) is not None and skin["ownershipType"] == "OWNED")
    # some skins in ownedSkins json might be rented so count owned skins manually
    seperatorCount = account["ownedSkins"].count(", ") 
    if seperatorCount > 0:
        account["ownedSkinsCount"] = seperatorCount + 1
    elif account["ownedSkins"]:
        account["ownedSkinsCount"] = 1
    else:
        account["ownedSkinsCount"] = 0

# obtains account's information on owned skins
def getChampions(leagueConnection, champions, account):
    ownedChampions = leagueConnection.get("/lol-champions/v1/owned-champions-minimal").json()
    account["ownedChampions"] = ", ".join(champions.getChampionById(champion["id"]) for champion in ownedChampions if champions.getChampionById(champion["id"]) is not None and champion["ownership"]["owned"])
    # owned champions endpoint includes free rotation champions so count owned champions manually
    seperatorCount = account["ownedChampions"].count(", ")
    if seperatorCount > 0:
        account["ownedChampionsCount"] = seperatorCount + 1
    elif account["ownedChampions"]:
        account["ownedChampionsCount"] = 1
    else:
        account["ownedChampionsCount"] = 0

# convert account's region to full name
def getFullRegion(account):
    regionFull = {
        "NA": "North America",
        "EUW": "Europe West",
        "RU": "Russia",
        "BR": "Brazil",
        "TR": "Turkey",
        "EUNE": "EU Nordic & East",
        "OC1": "Oceania",
        "LA2": "Latin America South",
        "LA1": "Latin America North",
    }

    account["regionFull"] = regionFull[account["region"]]

# obtain account's ranked stats on soloq and flexq modes
def getRank(leagueConnection, account):
    romanNumbers = {
        "IV": 4,
        "III": 3,
        "II": 2,
        "I": 1,
    }   

    rankedStats = leagueConnection.get("/lol-ranked/v1/current-ranked-stats").json()

    soloTier = ((rankedStats["queueMap"]["RANKED_SOLO_5x5"]["tier"]).lower()).capitalize()
    if soloTier == "None":
        account["soloTier"] = "Unranked"
        account["soloDivision"] = ""
        account["soloLP"] = ""
        account["soloWins"] = ""
        account["soloLosses"] = ""
        account["soloWinrate"] = ""
    else:
        account["soloTier"] = soloTier
        account["soloDivision"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["division"]
        account["soloLP"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["leaguePoints"]
        account["soloWins"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["wins"]
        account["soloLosses"] = rankedStats["queueMap"]["RANKED_SOLO_5x5"]["losses"]
        account["soloWinrate"] = round(account["soloWins"] / (account["soloWins"] + account["soloLosses"]) * 100)

    flexTier = ((rankedStats["queueMap"]["RANKED_FLEX_SR"]["tier"]).lower()).capitalize()
    if flexTier == "None":
        account["flexTier"] = "Unranked"
        account["flexDivision"] = ""
        account["flexLP"] = ""
        account["flexWins"] = ""
        account["flexLosses"] = ""
        account["flexWinrate"] = ""
    else:
        account["flexTier"] = flexTier
        account["flexDivision"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["division"]
        account["flexLP"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["leaguePoints"]
        account["flexWins"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["wins"]
        account["flexLosses"] = rankedStats["queueMap"]["RANKED_FLEX_SR"]["losses"]
        account["flexWinrate"] = round(account["flexWins"] / (account["flexWins"] + account["flexLosses"]) * 100)

# try to queue up and check if there's a low priority queue penalty
def getLowPriorityQueue(leagueConnection, account):
    queueArgs = {
        "queueId": 830, # Co-op vs. AI Intro Bot game
    }
    queueArgs = json.dumps(queueArgs, indent = 4)
    
    leagueConnection.post("/lol-lobby/v2/lobby", queueArgs)
    sleep(1)

    leagueConnection.post("/lol-lobby/v2/lobby/matchmaking/search")
    sleep(2)

    queueState = leagueConnection.get("/lol-lobby/v2/lobby/matchmaking/search-state").json()

    account["lowPriorityQueue"] = "Error" # unable to check low priority if the account has a dodge penalty or queue lockout

    if queueState["lowPriorityData"]["reason"] == "LEAVER_BUSTED":
        account["lowPriorityQueue"] = str(int(queueState["lowPriorityData"]["penaltyTime"] / 60)) + " minutes"
    elif queueState["searchState"] == "Found" or queueState["searchState"] == "Searching": # searching for game or found one (no penalties)
        account["lowPriorityQueue"] = "None"

# uses all data functions to get information about the account
def getData(leagueConnection, account, loot):
    getFullRegion(account)

    loot.refreshLoot()
    lootJson = loot.getLoot()
    getCurrencies(lootJson, account)
    
    getHonorLevel(leagueConnection, account)
    getSummoner(leagueConnection, account)
    getEmailVerification(leagueConnection, account)

    champions = Champions("data\\champions.json")
    getChampions(leagueConnection, champions, account)

    skins = Skins("data\\skins.json")
    getSkins(leagueConnection, loot, skins, account)

    getRank(leagueConnection, account)
    getLowPriorityQueue(leagueConnection, account)