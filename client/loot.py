from time import sleep
import re
from typing import Optional, List, Dict, Any
from client.connection.LeagueConnection import LeagueConnection

# Handles player loot.
class Loot:
    def __init__(self, leagueConnection: LeagueConnection):
        """
        Initializes the Loot instance.

        :param leagueConnection: An instance of LeagueConnection used for making API requests.
        """
        self.__leagueConnection = leagueConnection
        self.__allLoot = self.__leagueConnection.get("/lol-loot/v1/player-loot").json()

    def getLoot(self) -> List[Dict[str, Any]]:
        """
        Returns all the available loot.

        :return: A list of dictionaries representing the loot.
        """
        return self.__allLoot

    def getLootById(self, lootId: str) -> Optional[Dict[str, Any]]:
        """
        Returns the loot with the given ID, or None if it doesn't exist.

        :param lootId: The ID of the loot.

        :return: A dictionary representing the loot if found, None otherwise.
        """
        for loot in self.__allLoot:
            if loot["lootId"] == lootId:
                return loot
        
        return None

    def getLootCountById(self, lootId: str) -> int:
        """
        Returns the count of loot with the given ID, or 0 if there's no such loot.

        :param lootId: The ID of the loot.

        :return: The count of the loot.
        """
        lootCount = 0
        for loot in self.__allLoot:
            if loot["lootId"] == lootId:
                lootCount += loot["count"]
        
        return lootCount

    def getShardIdsByPattern(self, pattern: str) -> List[int]:
        """
        Returns shard IDs that match the given regex pattern.

        The pattern must have the ID in the second regex group.

        :param pattern: The regex pattern to match.

        :return: A list of shard IDs.
        """
        ids = []
        for loot in self.__allLoot:
            match = re.match(pattern, loot["lootId"])
            if match is not None:
                ids.append(int(match.group(1)))

        return ids
    
    def getLootByDisplayCategory(self, category: str) -> List[Dict[str, any]]:
        """
        Returns the loot with the matching display category.

        :param category: The display category to match.

        :return: A list of dictionaries representing the matching loot.
        """
        return [loot for loot in self.__allLoot if loot["displayCategories"] == category]

    def refreshLoot(self) -> None:
        """
        Refreshes the player's loot.

        This method should be used before performing a task with the loot to ensure up to date loot data.
        """
        self.__leagueConnection.post("/lol-loot/v1/refresh")
        sleep(2)
        self.__allLoot = self.__leagueConnection.get("/lol-loot/v1/player-loot").json()
