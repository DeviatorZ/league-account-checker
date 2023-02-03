
def getSummoner(leagueConnection, account):
    summoner = leagueConnection.get('/lol-summoner/v1/current-summoner')
    summoner = summoner.json()

    account["summonerLevel"] = summoner["summonerLevel"]
    account["ign"] = summoner["displayName"]

def getEmailVerification(leagueConnection, account):
    email = leagueConnection.get('/lol-email-verification/v1/email')
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