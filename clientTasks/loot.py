
def postRecipe(leagueConnection, recipeName, materials, repeat=1):
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)

def craftKeys(leagueConnection, loot):
    loot.refreshLoot()
    keyFragmentCount = loot.getLootCountById("MATERIAL_key_fragment")

    # 3 fragments required per key
    if keyFragmentCount >= 3:
        craftableKeyCount = keyFragmentCount // 3
        postRecipe(leagueConnection, "MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], repeat=craftableKeyCount)

def openChests(leagueConnection, loot):
    loot.refreshLoot()
    masterworkChestCount = loot.getLootCountById("CHEST_224")
    standardChestCount = loot.getLootCountById("CHEST_generic")
    masteryChestCount = loot.getLootCountById("CHEST_champion_mastery")
    keyCount = loot.getLootCountById("MATERIAL_key")

    # open masterwork chests first because they are better
    craftableChestCount = min(keyCount, masterworkChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConnection, "CHEST_224_OPEN", ["CHEST_224", "MATERIAL_key"], repeat=craftableChestCount)
        keyCount -= craftableChestCount

    craftableChestCount = min(keyCount, standardChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConnection, "CHEST_generic_OPEN", ["CHEST_generic", "MATERIAL_key"], repeat=craftableChestCount)
        keyCount -= craftableChestCount

    craftableChestCount = min(keyCount, masteryChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConnection, "CHEST_champion_mastery_OPEN", ["CHEST_champion_mastery", "MATERIAL_key"], repeat=craftableChestCount)