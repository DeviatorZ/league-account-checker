import json
from typing import Optional

class Champions:
    """
    Utility class for champion data, providing methods for loading and accessing champion information.
    """
    __championDict = {}

    @staticmethod
    def __loadData(filePath: str) -> None:
        """
        Internal method to load champion data from a JSON file.

        :param filePath: The path to the JSON file containing champion data.
        """
        with open(filePath, "r", encoding="utf8") as filePointer:
            championData = json.load(filePointer)

            for champion in championData:
                Champions.__championDict[champion["id"]] = champion["name"]

    @staticmethod
    def getChampionById(id: int) -> Optional[str]:
        """
        Retrieves the champion name associated with the specified ID.

        :param id: The ID of the champion.

        :return: The name of the champion if found, None otherwise.
        """
        return Champions.__championDict.get(id, None)
    
    @staticmethod
    def refreshData(filePath: str) -> None:
        """
        Refreshes the champion data by loading it from a JSON file.

        :param filePath: The path to the JSON file containing champion data.
        """
        Champions.__championDict.clear()
        Champions.__loadData(filePath)