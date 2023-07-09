from client.leagueStore.store import LoLStore
from client.champions import Champions
import logging
import heapq

def useFreeChampionRefunds(leagueStore: LoLStore, minPrice: int):
    """
    Refunds free champions purchased with BE.

    This function checks the purchase history in the League of Legends store and refunds any free champions that are refundable and were purchased with BE.
    The 'minPrice' parameter specifies the minimum price of a champion purchase to be eligible for refund.

    :param leagueStore: The League of Legends store object.
    :param minPrice: The minimum price of a champion purchase to be eligible for refund.
    """
    purchaseHistory = leagueStore.purchaseHistory

    for transaction in purchaseHistory["transactions"]:
        if transaction["refundable"] and transaction["currencyType"] == "IP" and not transaction.get("requiresToken", True):
            championName = Champions.getChampionById(transaction["itemId"])
            
            # isn't a champion
            if not championName:
                continue

            if transaction["amountSpent"] >= minPrice:
                logging.debug(f"Refunding champion(FREE): {championName}, BE: {transaction['amountSpent']}")
                leagueStore.refundTransaction(transaction["transactionId"], "CHAMPION")


def useRefundTokensOnChampions(leagueStore: LoLStore, minPrice: int):
    """
    Uses refund tokens to refund champions purchased with BE.

    This function checks the purchase history in the League of Legends store and uses refund tokens to refund champions that are refundable, were purchased with BE, and require a refund token.
    The 'minPrice' parameter specifies the minimum price of a champion purchase to be eligible for refund.
    It uses a priority queue (heap) to prioritize the champions based on their purchase price (most expensive first).

    :param leagueStore: The League of Legends store object.
    :param minPrice: The minimum price of a champion purchase to be eligible for refund.
    """
    purchaseHistory = leagueStore.purchaseHistory
    refundTokenCount = purchaseHistory["refundCreditsRemaining"]

    if refundTokenCount == 0:
        return
    
    itemHeap = []

    for transaction in purchaseHistory["transactions"]:
        if transaction["refundable"] and transaction["currencyType"] == "IP" and transaction.get("requiresToken", True):
            championName = Champions.getChampionById(transaction["itemId"])
            
            # isn't a champion
            if not championName:
                continue

            if transaction["amountSpent"] >= minPrice:
                heapq.heappush(itemHeap, (-transaction["amountSpent"], championName, transaction["transactionId"]))


    for _ in range(min(refundTokenCount, len(itemHeap))):
        price, championName, transactionId = heapq.heappop(itemHeap)
        logging.debug(f"Refunding champion(TOKEN): {championName}, BE: {-price}")
        leagueStore.refundTransaction(transactionId, "CHAMPION")