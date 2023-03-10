from time import sleep
import re

# handles player loot
class Loot():
    def __init__(self, leagueConnection):
        self.__leagueConnection = leagueConnection
        self.__allLoot = self.__leagueConnection.get("/lol-loot/v1/player-loot").json()

    def getLoot(self):
        return self.__allLoot

    # returns loot that has a given id, none if it doesn't exist
    def getLootById(self, lootId):
        for loot in self.__allLoot:
            if loot["lootId"] == lootId:
                return loot
        
        return None

    # returns loot count of given id, 0 if there's no such loot
    def getLootCountById(self, lootId):
        lootCount = 0
        for loot in self.__allLoot:
            if loot["lootId"] == lootId:
                lootCount += loot["count"]
        
        return lootCount

    # returns shards ids that match a given regex pattern (pattern must have the id in a 2nd regex group)
    def getShardIdsByPattern(self, pattern):
        ids = []
        for loot in self.__allLoot:
            match = re.match(pattern, loot["lootId"])
            if match is not None:
                ids.append(int(match.group(1)))

        return ids
    
    # returns loot with matching display category
    def getLootByDisplayCategory(self, category):
        return [loot for loot in self.__allLoot if loot["displayCategories"] == category]

    # refreshes loot (used after performing a task with loot)
    def refreshLoot(self):
        self.__leagueConnection.post("/lol-loot/v1/refresh")
        sleep(1)
        self.__allLoot = self.__leagueConnection.get("/lol-loot/v1/player-loot").json()


