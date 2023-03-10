from time import sleep

# claims event rewards
def claimEventRewards(leagueConnection):
    eventAvailable = leagueConnection.post("/lol-event-shop/v1/lazy-load-data")
    if eventAvailable is None:
        return
        
    leagueConnection.post("/lol-event-shop/v1/claim-select-all")

# buys an event shop offer by offer id
def buyOffer(leagueConnection, offerId):
    leagueConnection.post("/lol-event-shop/v1/purchase-offer", '{"offerId":"' + offerId + '"}')

# finds an offer that matches the price and id and spends as many tokens as possible on the offer
def buyOfferByPriceAndId(leagueConnection, price, id):
    eventAvailable = leagueConnection.post("/lol-event-shop/v1/lazy-load-data")
    if eventAvailable is None:
        return

    tokenShop = leagueConnection.get("/lol-event-shop/v1/categories-offers").json()

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

# spends tokens on champion shards
def buyChampionShardsWithTokens(leagueConnection):
    buyOfferByPriceAndId(leagueConnection, 50, "241")

# spends tokens on blue essence
def buyBlueEssenceWithTokens(leagueConnection):
    buyOfferByPriceAndId(leagueConnection, 1, "6")

