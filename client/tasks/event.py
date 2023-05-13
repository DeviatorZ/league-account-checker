from time import sleep
from client.connection.LeagueConnection import LeagueConnection

def claimEventRewards(leagueConnection: LeagueConnection):
    """
    Claims event rewards.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    """
    leagueConnection.post("/lol-event-shop/v1/claim-select-all")

def buyOffer(leagueConnection: LeagueConnection, offerId: str) -> None:
    """
    Buys an event shop offer by offer ID.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param offerId: The ID of the offer to buy.
    """
    leagueConnection.post("/lol-event-shop/v1/purchase-offer", '{"offerId":"' + offerId + '"}')

def buyOfferByPriceAndId(leagueConnection: LeagueConnection, price: int, id: str) -> None:
    """
    Finds an offer that matches the price and provides an item with the given ID and spends as many tokens as possible on the offer.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param price: The price of the offer in tokens.
    :param id: The ID of the item to buy.
    """
    tokenShop = leagueConnection.get("/lol-event-shop/v1/categories-offers").json()
    if tokenShop is None:
        return # token shop unavailable
    
    offerId = ""

    for offerCategory in tokenShop:
        if "category" in offerCategory:
            for offer in offerCategory["offers"]: 
                if offer["price"] == price and offer["items"][0]["itemId"] == id:
                    offerId = offer["id"]
                    break

    if offerId:
        balance = leagueConnection.get("/lol-event-shop/v1/token-balance").json()
        buyableCount = balance // price
        if buyableCount > 0:
            for _ in range(buyableCount):
                buyOffer(leagueConnection, offerId)
                sleep(1)

def buyChampionShardsWithTokens(leagueConnection: LeagueConnection) -> None:
    """
    Spends as many event tokens as possible on champion shards.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    """
    buyOfferByPriceAndId(leagueConnection, 50, "241")

def buyBlueEssenceWithTokens(leagueConnection: LeagueConnection) -> None:
    """
    Spends as many event tokens as possible on blue essence.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    """
    buyOfferByPriceAndId(leagueConnection, 1, "6")

