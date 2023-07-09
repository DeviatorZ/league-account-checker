from client.connection.LeagueConnection import LeagueConnection
import requests
import urllib3
from requests import Session
from requests import adapters
from client.leagueStore.exceptions import StoreException
from typing import Dict, Any
import logging
import time
import config
from functools import cached_property

class LoLStore(Session):
    """
    Class for interacting with the League of Legends store (online website).
    """
    def __init__(self, leagueConnection: LeagueConnection) -> None:
        """
        Initializes a LoLStore instance.

        :param leagueConnection: An instance of LeagueConnection used for making API requests.
        """
        self.__accountId = leagueConnection.get("/lol-summoner/v1/current-summoner").json()["accountId"]
        self.__accessToken = leagueConnection.get("/lol-rso-auth/v1/authorization/access-token").json()["token"]
        self.__requestHeaders = {"Authorization": f"Bearer {self.__accessToken}"}
        self.__storeURL = leagueConnection.get("/lol-store/v1/getStoreUrl").text.strip('"')
        self.__nextRequestTime = -1

        Session.__init__(self)
        retry = urllib3.util.retry.Retry(
            total = 3,
            respect_retry_after_header = True,
            backoff_factor = 1
        )

        adapter = adapters.HTTPAdapter(max_retries=retry)
        self.mount("https://", adapter)
        urllib3.disable_warnings()


    def __getRequestAccess(self) -> None:
        """
        Waits for the next available request.

        This method checks the current time against the next request time and waits until the next request access is available.
        Used to avoid getting rate limited.
        """
        while True:
            currentTime = time.time()
            sleepTime = self.__nextRequestTime - currentTime

            if sleepTime <= 0:
                self.__nextRequestTime = currentTime + config.LOL_STORE_REQUEST_COOLDOWN
                break
                
            time.sleep(sleepTime)

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        """
        Sends an HTTP request to the store.

        :param method: The HTTP method (e.g., GET, POST).
        :param url: The URL for the request.
        :param *args: Additional positional arguments for the request.
        :param **kwargs: Additional keyword arguments for the request.

        :return: A requests.Response object representing the HTTP response.

        Raises:
            StoreException: If there's an issue with the request.
        """
        self.__getRequestAccess()

        try:
            logging.debug(f"{method} : {url} : {args} {kwargs}")
        except Exception as e:
            logging.debug(e)

        url = self.__storeURL + url
        kwargs["headers"] = self.__requestHeaders
        try:
            response = Session.request(self, method, url, *args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise StoreException(f"RequestException: {e}")

        if response.ok:
            return response
        
        raise StoreException(f"Unexpected response code: {url} : {response.status_code}")
    
    @cached_property
    def purchaseHistory(self) -> Dict[str, Any]:
        """
        Retrieves the purchase history.

        :return: A dictionary containing the purchase history.
        """
        return self.get("/storefront/v3/history/purchase").json()

    def refundTransaction(self, transactionId: str, inventoryType: str) -> None:
        """
        Refunds a transaction in the store.

        :param transactionId: The ID of the transaction to be refunded.
        :param inventoryType: The type of inventory to refund the transaction from. Example: "CHAMPION"
        """
        data = {
            "accountId": self.__accountId,
            "transactionId": transactionId,
            "inventoryType": inventoryType,
        }
        self.post("/storefront/v3/refund", json=data)