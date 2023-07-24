import json
from typing import Optional

class LootData:
    """
    Utility class for loot data, providing methods for loading and accessing loot information.
    """
    __lootDict = {}

    @staticmethod
    def __loadData(filePath: str) -> None:
        """
        Internal method to load loot data from a JSON file.

        :param filePath: The path to the JSON file containing loot data.
        """
        with open(filePath, "r", encoding="utf8") as filePointer:
            LootData.__lootDict = json.load(filePointer)
            
    @staticmethod
    def getLootById(id: int) -> Optional[str]:
        """
        Retrieves the loot name associated with the specified ID.

        :param id: The ID of the loot.

        :return: The name of the loot if found, None otherwise.
        """
        name = LootData.__lootDict.get(f"loot_name_{id.lower()}")
        if name:
            return name
        return LootData.__lootDict.get(id)
    
    @staticmethod
    def refreshData(filePath: str) -> None:
        """
        Refreshes the loot data by loading it from a JSON file.

        :param filePath: The path to the JSON file containing loot data.
        """
        LootData.__lootDict.clear()
        LootData.__loadData(filePath)