from clientTasks.api import craftRecipe
import logging

def craftKeys(leagueConection, loot):
    loot.refreshLoot()
    keyFragments = loot.getLootById("MATERIAL_key_fragment")["count"]

    logging.info(keyFragments)
    if keyFragments >= 3:
        craftableKeyCount = keyFragments // 3
        craftRecipe("MATERIAL_key_fragment_forge", ["MATERIAL_key_fragment"], craftableKeyCount)