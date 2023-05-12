import re
from time import sleep
from client.loot import Loot
from client.connection.LeagueConnection import LeagueConnection
from typing import List

def postRecipe(leagueConnection: LeagueConnection, recipeName: str, materials: List[str], repeat: int = 1) -> None:
    """
    Posts a recipe with the given name, materials, and repeat count.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param recipeName: The name of the recipe to post.
    :param materials: A list of material names.
    :param repeat: The number of times to repeat the recipe (default is 1).
    """
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)

def craftKeys(leagueConnection: LeagueConnection, loot: Loot) -> None:
    """
    Crafts Hextech keys using available key fragments.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    keyFragmentCount = loot.getLootCountById("MATERIAL_key_fragment")

    # 3 fragments required per key
    if keyFragmentCount >= 3:
        craftableKeyCount = keyFragmentCount // 3
        postRecipe(leagueConnection, "MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], repeat=craftableKeyCount)

def openChests(leagueConnection: LeagueConnection, loot: Loot) -> None:
    """
    Opens all Hextech chests available on the account.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    """
    while True:
        loot.refreshLoot()
        masterworkChestCount = loot.getLootCountById("CHEST_224")
        standardChestCount = loot.getLootCountById("CHEST_generic")
        masteryChestCount = loot.getLootCountById("CHEST_champion_mastery")
        keyCount = loot.getLootCountById("MATERIAL_key")

        if masterworkChestCount + standardChestCount + masteryChestCount == 0 or keyCount == 0:
            return

        # Open masterwork chests first because they are better
        craftableChestCount = min(keyCount, masterworkChestCount)
        if craftableChestCount > 0:
            postRecipe(leagueConnection, "CHEST_224_OPEN", ["CHEST_224", "MATERIAL_key"], repeat=craftableChestCount)
            sleep(1)
            keyCount -= craftableChestCount

        craftableChestCount = min(keyCount, standardChestCount)
        if craftableChestCount > 0:
            postRecipe(leagueConnection, "CHEST_generic_OPEN", ["CHEST_generic", "MATERIAL_key"], repeat=craftableChestCount)
            sleep(1)
            keyCount -= craftableChestCount

        craftableChestCount = min(keyCount, masteryChestCount)
        if craftableChestCount > 0:
            postRecipe(leagueConnection, "CHEST_champion_mastery_OPEN", ["CHEST_champion_mastery", "MATERIAL_key"], repeat=craftableChestCount)
            sleep(1)

def openLoot(leagueConnection: LeagueConnection, loot: Loot) -> None:
    """
    Opens all non-Hextech chest loot available on the account.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    notHextechChest = "CHEST_((?!(224|generic|champion_mastery)).)*"
    allLoot = loot.getLoot()

    lootToOpen = [currentLoot for currentLoot in allLoot if re.fullmatch(notHextechChest, currentLoot["lootId"])]

    for currentLoot in lootToOpen:
        name, count = currentLoot["lootName"], currentLoot["count"]
        postRecipe(leagueConnection, f"{name}_OPEN", [name], repeat=count)
        sleep(1)