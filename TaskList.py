from clientTasks.event import claimEventRewards
from clientTasks.event import buyChampionShardsWithTokens
from clientTasks.event import buyBlueEssenceWithTokens
from clientTasks.crafting import craftKeys
from clientTasks.crafting import openChests
from clientTasks.crafting import openLoot
from clientTasks.disenchanting import disenchantChampionShards
from clientTasks.disenchanting import disenchantEternalsShards


class TaskList():
    _eventTasks = {
        "claimEventRewards" :
        {
            "text" : "Claim event rewards",
            "requiresLoot" : False,
            "function" : claimEventRewards,
        },
        "buyChampionShardsWithTokens" :
        {
            "text" : "Buy champion shards",
            "requiresLoot" : False,
            "function" : buyChampionShardsWithTokens,
        },
        "buyBlueEssenceWithTokens" :
        {
            "text" : "Buy BE",
            "requiresLoot" : False,
            "function" : buyBlueEssenceWithTokens,
        },
    }

    _craftingTasks = {
        "craftKeys" : 
        {
            "text" : "Craft hextech keys",
            "requiresLoot" : True,
            "function" : craftKeys,
        },
        "openChests" :
        {
            "text" : "Open hextech chests",
            "requiresLoot" : True,
            "function" : openChests,
        },
        "openLoot" :
        {
            "text" : "Open capsules, orbs, random shards",
            "requiresLoot" : True,
            "function" : openLoot,
        },
    }

    _disenchantingTasks = {
        "disenchantChampionShards" :
        {
            "text" : "Champion shards",
            "requiresLoot" : True,
            "function" : disenchantChampionShards,
        },
        "disenchantEternalsShards" :
        {
            "text" : "Eternals shards",
            "requiresLoot" : True,
            "function" : disenchantEternalsShards,
        },
    }

    _allTasks = {**_eventTasks, **_craftingTasks, **_disenchantingTasks}

    @staticmethod
    def getTaskDisplay():
        eventTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._eventTasks.items()}
        craftingTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._craftingTasks.items()}
        disenchantingTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._disenchantingTasks.items()}
        return {
            "Event Shop" : eventTasks,
            "Crafting" : craftingTasks,
            "Disenchanting" : disenchantingTasks,
        }

    @staticmethod
    def getTasks(leagueConnection, loot):
        tasks = {}

        for taskName, taskOptions in TaskList._allTasks.items():
            tasks[taskName] = {"function" : taskOptions["function"]}
            
            if taskOptions["requiresLoot"]:
                tasks[taskName]["args"] = [leagueConnection, loot]
            else:
                tasks[taskName]["args"] = [leagueConnection]

        return tasks