from client.tasks.crafting import postRecipe
from time import sleep
from client.connection.LeagueConnection import LeagueConnection
from client.loot import Loot

def disenchantChampionShards(leagueConnection: LeagueConnection, loot: Loot) -> None:
    """
    Disenchants all champion shards.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("CHAMPION")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount = shard["type"], [shard["lootName"]], shard["count"]
        # _disenchant is case-sensitive
        postRecipe(leagueConnection, f"{shardType}_disenchant", shardData, shardCount)
        sleep(1)

def disenchantEternalsShards(leagueConnection: LeagueConnection, loot: Loot) -> None:
    """
    Disenchants all eternals shards.

    :param leagueConnection: An instance of LeagueConnection used for making API requests.
    :param loot: An instance of Loot for accessing loot data.
    """
    loot.refreshLoot()
    shardsToDisenchant = loot.getLootByDisplayCategory("ETERNALS")

    for shard in shardsToDisenchant:
        shardType, shardData, shardCount = shard["type"], [shard["lootName"]], shard["count"]
        # _DISENCHANT is case-sensitive
        postRecipe(leagueConnection, f"{shardType}_DISENCHANT", shardData, shardCount)
        sleep(1)