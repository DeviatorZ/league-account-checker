from time import sleep

def claimEventRewards(leagueConnection):
    leagueConnection.post("/lol-event-shop/v1/lazy-load-data")
    leagueConnection.post("/lol-event-shop/v1/claim-select-all")

def buyOffer(leagueConnection, offerId):
    leagueConnection.post("/lol-event-shop/v1/purchase-offer", '{"offerId":"' + offerId + '"}')

def buyOfferByPriceAndId(leagueConnection, price, id):
    leagueConnection.post("/lol-event-shop/v1/lazy-load-data")
    tokenShop = leagueConnection.get("/lol-event-shop/v1/categories-offers").json()

    offerId = ""

    for offerCategory in tokenShop:
        if "category" in offerCategory:
            if offerCategory["category"] == "Loot":
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

def buyChampionShardsWithTokens(leagueConnection):
    buyOfferByPriceAndId(leagueConnection, 50, "241")

def buyBlueEssenceWithTokens(leagueConnection):
    buyOfferByPriceAndId(leagueConnection, 1, "6")

