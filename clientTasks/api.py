
def craftRecipe(leagueConnection, recipeName, materials, repeat=1):
    leagueConnection.post(f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}", json=materials)