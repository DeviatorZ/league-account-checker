from client.tasks.event import claimEventRewards
from client.tasks.event import buyChampionShardsWithTokens
from client.tasks.event import buyBlueEssenceWithTokens
from client.tasks.crafting import craftKeys
from client.tasks.crafting import openChests
from client.tasks.crafting import openLoot
from client.tasks.disenchanting import disenchantChampionShards
from client.tasks.disenchanting import disenchantEternalsShards
from typing import Dict, Any, List, Callable, Union
from client.connection.LeagueConnection import LeagueConnection
from client.loot import Loot

class TaskList:
    _eventTasks: Dict[str, Dict[str, Any]] = {
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

    _craftingTasks: Dict[str, Dict[str, Any]] = {
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

    _disenchantingTasks: Dict[str, Dict[str, Any]] = {
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

    _allTasks: Dict[str, Dict[str, Any]] = {**_eventTasks, **_craftingTasks, **_disenchantingTasks}

    @staticmethod
    def getTaskDisplay() -> Dict[str, Dict[str, str]]:
        """
        Builds and returns a dictionary of task categories with their respective task names and descriptions for GUI display.

        :return: a dictionary of task categories with their respective task names and descriptions
        """
        eventTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._eventTasks.items()}
        craftingTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._craftingTasks.items()}
        disenchantingTasks = {key: {"text" : value["text"]} for (key, value) in TaskList._disenchantingTasks.items()}
        return {
            "Event Shop" : eventTasks,
            "Crafting" : craftingTasks,
            "Disenchanting" : disenchantingTasks,
        }

    @staticmethod
    def getTasks(leagueConnection: LeagueConnection, loot: Loot) -> Dict[str, Dict[str, Union[Callable, List[Union[LeagueConnection, Loot]]]]]:
        """
        Builds and returns a task dictionary for a given client.

        :param leagueConnection: An instance of LeagueConnection used for making API requests.
        :param loot: An instance of Loot for accessing loot data.

        Returns:
        - tasks (Dict[str, Dict[str, Union[Callable, List[Union[LeagueConnection, Loot]]]]]): A dictionary of tasks with the following structure:
            {
                taskName1: {
                    "function": function1,
                    "args": [leagueConnection, loot] or [leagueConnection]
                },
                taskName2: {
                    "function": function2,
                    "args": [leagueConnection, loot] or [leagueConnection]
                },
                ...
            }
        - taskName (str): A name of the task to perform.
        - function (Callable): A function to perform a task.
        - args (List[Union[LeagueConnection, Loot]]): A list of arguments for the task function.

        """
        tasks = {}

        for taskName, taskOptions in TaskList._allTasks.items():
            tasks[taskName] = {"function" : taskOptions["function"]}
            
            if taskOptions["requiresLoot"]:
                tasks[taskName]["args"] = [leagueConnection, loot]
            else:
                tasks[taskName]["args"] = [leagueConnection]

        return tasks