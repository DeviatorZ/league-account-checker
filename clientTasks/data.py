import json

class Champions():
    def __init__(self, path):
        with open(path, "r", encoding="utf8") as filePointer:
            self.championData = json.load(filePointer)

            self.championById = {}
            for champion in self.championData:
                self.championById[champion["id"]] = champion["name"]

    def getChampionById(self, id):
        return self.championById[id]

class Skins():
    def __init__(self, path):
        with open(path, "r", encoding="utf8") as filePointer:
            self.skinById = json.load(filePointer)

    def getSkinById(self, id):
        try:
            return self.skinById[str(id)]["name"]
        except:
            return None

def getSummoner(leagueConnection, account):
    summoner = leagueConnection.get("/lol-summoner/v1/current-summoner")
    summoner = summoner.json()

    account["summonerLevel"] = summoner["summonerLevel"]
    account["ign"] = summoner["displayName"]

def getEmailVerification(leagueConnection, account):
    email = leagueConnection.get("/lol-email-verification/v1/email")
    email = email.json()

    if email["emailVerified"]:
        account["emailVerified"] = "Verified"
    else:
        account["emailVerified"] = "Unverified"

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

def getSkins(leagueConnection ,loot, skins, account):
    skinShardsRental = loot.getShardIdsByPattern("CHAMPION_SKIN_RENTAL_(\d+)")
    account["skinShardsRental"]= ", ".join(skins.getSkinById(id) for id in skinShardsRental if skins.getSkinById(id) is not None)
    account["skinShardsRentalCount"] = len(skinShardsRental)

    skinShardsPermanent = loot.getShardIdsByPattern("CHAMPION_SKIN_(\d+)")
    account["skinShardsPermanent"]= ", ".join(skins.getSkinById(id) for id in skinShardsPermanent if skins.getSkinById(id) is not None)
    account["skinShardsPermanentCount"] = len(skinShardsPermanent)

    ownedSkins = leagueConnection.get("/lol-inventory/v2/inventory/CHAMPION_SKIN").json()
    account["ownedSkins"] = ", ".join(skins.getSkinById(skin["itemId"]) for skin in ownedSkins if skins.getSkinById(skin["itemId"]) is not None and skin["ownershipType"] == "OWNED")
    account["ownedSkinsCount"] = account["ownedSkins"].count(", ") + 1
        
def getData(leagueConnection, account, loot):
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

    romanNumbers = {
        "IV": 4,
        "III": 3,
        "II": 2,
        "I": 1,
    }

    account["regionFull"] = regionFull[account["region"]]

    loot.refreshLoot()
    lootJson = loot.getLoot()
    getCurrencies(lootJson, account)

    getSummoner(leagueConnection, account)
    getEmailVerification(leagueConnection, account)

    champions = Champions("champions.json")
    
    skins = Skins("skins.json")
    getSkins(leagueConnection, loot, skins, account)