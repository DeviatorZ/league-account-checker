
def postRecipe(leagueConnection, recipeName, materials, repeat=1):
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)

def craftKeys(leagueConection, loot):
    loot.refreshLoot()
    keyFragments = loot.getLootById("MATERIAL_key_fragment")["count"]

    if keyFragments >= 3:
        craftableKeyCount = keyFragments // 3
        postRecipe(leagueConection, "MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], craftableKeyCount)