from clientTasks.crafting import postRecipe
from time import sleep

def disenchantChampionShards(leagueConnection, loot):
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("CHAMPION")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount,  = shard["type"], [shard["lootName"]], shard["count"]
        postRecipe(leagueConnection, f"{shardType}_disenchant", shardData, shardCount)
        sleep(1) 

def disenchantEternalsShards(leagueConnection, loot):
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("ETERNALS")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount,  = shard["type"], [shard["lootName"]], shard["count"]
        postRecipe(leagueConnection, f"{shardType}_DISENCHANT", shardData, shardCount)
        sleep(1) 