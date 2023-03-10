from client.tasks.crafting import postRecipe
from time import sleep

# disenchant recipes are case sensitive. Append "_disenchant" for champion shards, "_DISENCHANT" for eternals shards

# disenchants all champions shards
def disenchantChampionShards(leagueConnection, loot):
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("CHAMPION")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount,  = shard["type"], [shard["lootName"]], shard["count"]
        postRecipe(leagueConnection, f"{shardType}_disenchant", shardData, shardCount)
        sleep(1) 

# disenchants all eternals shards
def disenchantEternalsShards(leagueConnection, loot):
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("ETERNALS")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount,  = shard["type"], [shard["lootName"]], shard["count"]
        postRecipe(leagueConnection, f"{shardType}_DISENCHANT", shardData, shardCount)
        sleep(1) 