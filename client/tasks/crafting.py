import re
from time import sleep

# post a recipe with given name, materials and amount
def postRecipe(leagueConnection, recipeName, materials, repeat=1):
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)

# crafts hextech keys
def craftKeys(leagueConnection, loot):
    loot.refreshLoot()
    keyFragmentCount = loot.getLootCountById("MATERIAL_key_fragment")

    # 3 fragments required per key
    if keyFragmentCount >= 3:
        craftableKeyCount = keyFragmentCount // 3
        postRecipe(leagueConnection, "MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], repeat=craftableKeyCount)

# opens all chests on an account
def openChests(leagueConnection, loot):

    # keep opening just in case more chests dropped from chests
    while True:
        loot.refreshLoot()
        masterworkChestCount = loot.getLootCountById("CHEST_224")
        standardChestCount = loot.getLootCountById("CHEST_generic")
        masteryChestCount = loot.getLootCountById("CHEST_champion_mastery")
        keyCount = loot.getLootCountById("MATERIAL_key")

        if masterworkChestCount + standardChestCount + masteryChestCount == 0 or keyCount == 0:
            return

        # open masterwork chests first because they are better
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

# opens all loot expect for chests
def openLoot(leagueConnection, loot):
    loot.refreshLoot()
    notHextechChest = "CHEST_((?!(224|generic|champion_mastery)).)*"
    allLoot = loot.getLoot()

    lootToOpen = [currentLoot for currentLoot in allLoot if re.fullmatch(notHextechChest, currentLoot["lootId"])]

    for currentLoot in lootToOpen:
        name, count = currentLoot["lootName"], currentLoot["count"]
        postRecipe(leagueConnection, f"{name}_OPEN", [name], repeat=count)
        sleep(1)