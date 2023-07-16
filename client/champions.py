import json
from typing import Optional, List

class Champions:
    """
    Utility class for champion data, providing methods for loading and accessing champion information.
    """
    __ChampionIdDict = {}
    __ChampionNameDict = {}

    @staticmethod
    def __loadData(filePath: str) -> None:
        """
        Internal method to load champion data from a JSON file.

        :param filePath: The path to the JSON file containing champion data.
        """
        with open(filePath, "r", encoding="utf8") as filePointer:
            championData = json.load(filePointer)

            for champion in championData:
                if champion["id"] > 0:
                    Champions.__ChampionIdDict[champion["id"]] = champion["name"]
                    Champions.__ChampionNameDict[champion["name"]] = champion["id"]

    @staticmethod
    def getChampionById(id: int) -> Optional[str]:
        """
        Retrieves the champion name associated with the specified ID.

        :param id: The ID of the champion.

        :return: The name of the champion if found, None otherwise.
        """
        return Champions.__ChampionIdDict.get(id, None)
    
    @staticmethod
    def getChampionIdByName(name: str) -> Optional[int]:
        """
        Retrieves the champion ID associated with the specified name.

        :param name: The name of the champion.

        :return: The ID of the champion if found, None otherwise.
        """
        return Champions.__ChampionNameDict.get(name, None)
    
    @staticmethod
    def refreshData(filePath: str) -> None:
        """
        Refreshes the champion data by loading it from a JSON file.

        :param filePath: The path to the JSON file containing champion data.
        """
        Champions.__ChampionIdDict.clear()
        Champions.__ChampionNameDict.clear()
        Champions.__loadData(filePath)

    @staticmethod
    def getAllChampions() -> List[str]:
        """
        Provides all champion names

        :return: A list of all champion names
        """
        return list(Champions.__ChampionIdDict.values())