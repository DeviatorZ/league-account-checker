from client.connection.exceptions import AccountBannedException
from client.connection.exceptions import AuthenticationException
from client.connection.RiotConnection import RiotConnection
from client.connection.LeagueConnection import LeagueConnection
from client.loot import Loot
from client.tasks.data import getData
from client.tasks.buyChampions import buyChampions
from data.TaskList import TaskList
from accountProcessing.exceptions import RateLimitedException
from datetime import datetime
from time import sleep
from typing import Dict, Any
import logging
import json
from client.leagueStore.refunding import useFreeChampionRefunds
from client.leagueStore.refunding import useRefundTokensOnChampions
from client.leagueStore.store import LoLStore
import GUI.keys as guiKeys
import config


class LeagueOfLegendsWorker:

    def __init__(self, account: Dict[str, Any], settings: Dict[str, Any], allowPatching: bool, headless: bool, riotPort: int, leaguePort: int) -> None:
        """
        Initializes a LeagueOfLegendsWorker instance.

        :param account: A dictionary containing account information such as username, password, region, and state.
        :param settings: A dictionary containing worker settings such as tasks to run and export type.
        :param allowPatching: A boolean that determines whether patching is allowed.
        :param headless: Flag indicating whether to run the client headless or not.
        :param riotPort: An integer representing the port for RiotConnection.
        :param leaguePort: An integer representing the port for LeagueConnection.
        """
        self.__settings = settings
        self.__allowPatching = allowPatching
        self.__account = account
        self.__riotPort = riotPort
        self.__leaguePort = leaguePort
        self.__headless = headless

    def __enter__(self):
        self.__riotConnection = None
        self.__leagueConnection = None
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Terminates league/riot client process on exit.
        """
        if self.__leagueConnection is not None:
            self.__leagueConnection.kill()
        elif self.__riotConnection is not None:
            self.__riotConnection.kill()

    def handleRiotClient(self) -> str:
        """
        Handles the Riot client connection and login.

        :return: The state of the account after handling the Riot client.
        """
        self.__riotConnection = RiotConnection(self.__settings[guiKeys.RIOT_CLIENT], self.__riotPort, self.__allowPatching)

        try:
            self.__riotConnection.login(self.__account["username"], self.__account["password"], self.__settings)
            self.__account["region"] = self.__riotConnection.get("/riotclient/region-locale").json()["region"]
        except AuthenticationException as exception:
            if exception.error == "RATE_LIMITED": # rate limited due too many accounts with incorrect credentials
                raise RateLimitedException("Too many login attempts")
            elif exception.error == "CREDENTIALS_400":
                raise RateLimitedException("Too many login attempts or 'Stay signed in' is enabled")
            else: # wrong credentials / account needs updating
                logging.error(f"{self.__account['username']} AuthenticationException: {exception.error}")
                return exception.error

        return "OK"

    def handleLeagueClient(self) -> str:
        """
        Handles the League client connection and session.

        :return: The state of the account after handling the League client.
        """
        try:
            self.__leagueConnection = LeagueConnection(self.__settings[guiKeys.LEAGUE_CLIENT], self.__riotConnection, self.__account["region"], self.__leaguePort, self.__allowPatching, self.__headless)
            self.__leagueConnection.waitForSession()
        except AccountBannedException as ban:
            # add ban information to the account for export
            banDescription = json.loads(ban.error["description"])
            self.__account["banReason"] = banDescription["restrictions"][0]["reason"]

            if banDescription["restrictions"][0]["type"] != "PERMANENT_BAN":
                banExpiration = banDescription["restrictions"][0]["dat"]["expirationMillis"]
                self.__account["banExpiration"] = datetime.utcfromtimestamp(banExpiration / 1000).strftime(config.DATE_FORMAT) # banExpiration is unix timestamp in miliseconds
            else:
                self.__account["banExpiration"] = "PERMANENT"

            logging.error(f"{self.__account['username']} AccountBannedException - Reason:{self.__account['banReason']}, Expiration:{self.__account['banExpiration']}")
            return "BANNED"
        
        return "OK"

    def performTasks(self) -> None:
        """
        Performs the tasks based on settings.
        """
        loot = Loot(self.__leagueConnection)
        self.__runGeneralTasks(loot)
        self.__runStoreTasks()
        sleep(2)

        if self.__settings[guiKeys.BUY_CHAMPIONS]:
            buyChampions(self.__leagueConnection, loot, self.__settings[guiKeys.CHAMPION_SHOP_PURCHASE_LIST], self.__settings[guiKeys.MAXIMUM_OWNED_CHAMPIONS])

        # obtain extra account information if it's not set to minimal type
        if not self.__settings[guiKeys.EXPORT_MINIMAL]:
            getData(self.__leagueConnection, self.__account, loot, self.__settings[guiKeys.SKIP_LOW_PRIO_CHECK])

    def __runGeneralTasks(self, loot: Loot) -> None:
        tasks = TaskList.getTasks(self.__leagueConnection, loot)

        # run tasks
        for taskName, task in tasks.items():
            if self.__settings[taskName]:
                task["function"](*task["args"])
                sleep(2) # allow loot to update between tasks

    def __runStoreTasks(self) -> None:
        """
        Performs tasks on the League store.
        """
        if not (self.__settings[guiKeys.USE_FREE_CHAMPION_REFUNDS] or self.__settings[guiKeys.USE_TOKEN_CHAMPION_REFUNDS]):
            return
        
        leagueStore = LoLStore(self.__leagueConnection)

        if self.__settings[guiKeys.USE_FREE_CHAMPION_REFUNDS]:
            useFreeChampionRefunds(leagueStore, int(self.__settings[guiKeys.USE_FREE_CHAMPION_REFUNDS_MIN_PRICE_BE]))

        if self.__settings[guiKeys.USE_TOKEN_CHAMPION_REFUNDS]:
            useRefundTokensOnChampions(leagueStore, int(self.__settings[guiKeys.USE_TOKEN_CHAMPION_REFUNDS_MIN_PRICE_BE]))
            