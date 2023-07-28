import json
from typing import Optional

class LootData:
    """
    Utility class for loot data, providing methods for loading and accessing loot information.
    """
    __lootDataDict = {}
    __lootItemsDict = {}

    @staticmethod
    def __loadData(filePathLootData: str, filePathLootItems: str) -> None:
        """
        Internal method to load loot data from a JSON file.

        :param filePath: The path to the JSON file containing loot data.
        """
        with open(filePathLootData, "r", encoding="utf8") as filePointer:
            LootData.__lootDataDict = json.load(filePointer)

        with open(filePathLootItems, "r", encoding="utf8") as filePointer:
            lootItems = json.load(filePointer)
            
            for item in lootItems["LootItems"]:
                LootData.__lootItemsDict[item["id"]] = item["name"]
                
    @staticmethod
    def getLootById(id: int) -> Optional[str]:
        """
        Retrieves the loot name associated with the specified ID.

        :param id: The ID of the loot.

        :return: The name of the loot if found, None otherwise.
        """
        return LootData.__lootDataDict.get(f"loot_name_{id.lower()}") or LootData.__lootDataDict.get(id) or LootData.__lootItemsDict.get(id)

    
    @staticmethod
    def refreshData(filePathLootData: str, filePathLootItems: str) -> None:
        """
        Refreshes the loot data by loading it from a JSON file.

        :param filePath: The path to the JSON file containing loot data.
        """
        LootData.__lootDataDict.clear()
        LootData.__lootItemsDict.clear()
        LootData.__loadData(filePathLootData, filePathLootItems)