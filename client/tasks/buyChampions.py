from copy import deepcopy
from client.connection.LeagueConnection import LeagueConnection
from client.loot import Loot
from typing import List, Dict
from client.champions import Champions

ITEM_SCHEMA = {
    "itemKey": {
        "inventoryType": "CHAMPION",
        "itemId": -1
    },
    "purchaseCurrencyInfo": {
        "currencyType": "IP",
        "price": -1,
        "purchasable": True
    },
    "quantity": 1,
    "source": "cdp"
}

def getChampionPrices(leagueConnection: LeagueConnection) -> Dict[str, int]:
    """
    Retrieves the prices of champions from the League of Legends shop (BE).

    :param leagueConnection: An instance of LeagueConnection used for making API requests.

    :return: A dictionary mapping champion IDs to their prices.
    """
    shopCatalog = leagueConnection.get("/lol-catalog/v1/items/CHAMPION").json()
    prices = {}

    for item in shopCatalog:
        for purchaseMethod in item["prices"]:
            if purchaseMethod["currency"] == "IP":
                prices[item["itemId"]] = purchaseMethod["cost"]

    return prices

def buyChampions(leagueConnection: LeagueConnection, loot: Loot, purchaseList: List[str], maxOwnedChampions: int) -> None:
    """
    Buys champions from the shop.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    :purchaseList: A list of champion names to purchase.
    :maxOwnedChampions:: The maximum number of champions the player can own. No more purchases after reaching this limit.
    """
    purchaseRequestJson = {
        "items": []
    }

    priceDict = getChampionPrices(leagueConnection)
    ownedChampions = leagueConnection.get("/lol-champions/v1/owned-champions-minimal").json()
    ownedChampionList = [champion["id"] for champion in ownedChampions if champion["ownership"]["owned"]]

    loot.refreshLoot()
    be = loot.getLootCountById("CURRENCY_champion")
    
    for championName in purchaseList:
        championId = Champions.getChampionIdByName(championName)
        championPrice = priceDict[championId]
        if be - championPrice >= 0 and len(ownedChampionList) < maxOwnedChampions:
            if championId in ownedChampionList:
                continue
            be -= championPrice
            ownedChampionList.append(championId)
            purchaseItem = deepcopy(ITEM_SCHEMA)
            purchaseItem["itemKey"]["itemId"] = championId
            purchaseItem["purchaseCurrencyInfo"]["price"] = championPrice
            
            purchaseRequestJson["items"].append(purchaseItem)
        else:
            break

    if len(purchaseRequestJson["items"]) > 0:
        leagueConnection.post("/lol-purchase-widget/v2/purchaseItems", json=purchaseRequestJson)





