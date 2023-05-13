import json
from typing import Optional

class Skins:
    """
    Utility class for skin data, providing methods for loading and accessing skin information.
    """
    __skinDict = {}

    @staticmethod
    def __loadData(filePath: str) -> None:
        """
        Internal method to load skin data from a JSON file.

        :param filePath: The path to the JSON file containing skin data.
        """
        with open(filePath, "r", encoding="utf8") as filePointer:
            skinData = json.load(filePointer)

            for skin in skinData.values():
                Skins.__skinDict[skin["id"]] = skin["name"]

    @staticmethod
    def getSkinById(id: int) -> Optional[str]:
        """
        Retrieves the skin name associated with the specified ID.

        :param id: The ID of the skin.

        :return: The name of the skin if found, None otherwise.
        """
        return Skins.__skinDict.get(id, None)
    
    @staticmethod
    def refreshData(filePath: str) -> None:
        """
        Refreshes the skin data by loading it from a JSON file.

        :param filePath: The path to the JSON file containing skin data.
        """
        Skins.__skinDict.clear()
        Skins.__loadData(filePath)