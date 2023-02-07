
def postRecipe(leagueConnection, recipeName, materials, repeat=1):
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)

def craftKeys(leagueConection, loot):
    loot.refreshLoot()
    keyFragmentCount = loot.getLootCountById("MATERIAL_key_fragment")

    if keyFragmentCount >= 3:
        craftableKeyCount = keyFragmentCount // 3
        postRecipe(leagueConection, "MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], repeat=craftableKeyCount)

def openChests(leagueConection, loot):
    loot.refreshLoot()
    masterworkChestCount = loot.getLootCountById("CHEST_224")
    standardChestCount = loot.getLootCountById("CHEST_generic")
    masteryChestCount = loot.getLootCountById("CHEST_champion_mastery")
    keyCount = loot.getLootCountById("MATERIAL_key")

    craftableChestCount = min(keyCount, masterworkChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConection, "CHEST_224_OPEN", ["CHEST_224", "MATERIAL_key"], repeat=craftableChestCount)
        keyCount -= craftableChestCount

    craftableChestCount = min(keyCount, standardChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConection, "CHEST_generic_OPEN", ["CHEST_generic", "MATERIAL_key"], repeat=craftableChestCount)
        keyCount -= craftableChestCount

    craftableChestCount = min(keyCount, masteryChestCount)
    if craftableChestCount > 0:
        postRecipe(leagueConection, "CHEST_champion_mastery_OPEN", ["CHEST_champion_mastery", "MATERIAL_key"], repeat=craftableChestCount)