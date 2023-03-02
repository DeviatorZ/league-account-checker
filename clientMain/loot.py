from time import time
from time import sleep
import re

# handles player loot
class Loot():
    def __init__(self, leagueConnection):
        self.leagueConnection = leagueConnection
        self.allLoot = self.leagueConnection.get("/lol-loot/v1/player-loot").json()

    def getLoot(self):
        return self.allLoot

    # returns loot that has a given id, none if it doesn't exist
    def getLootById(self, lootId):
        for loot in self.allLoot:
            if loot["lootId"] == lootId:
                return loot
        
        return None

    # returns loot count of given id, 0 if there's no such loot
    def getLootCountById(self, lootId):
        lootCount = 0
        for loot in self.allLoot:
            if loot["lootId"] == lootId:
                lootCount += loot["count"]
        
        return lootCount

    # returns shards ids that match a given regex pattern (pattern must have the id in a 2nd regex group)
    def getShardIdsByPattern(self, pattern):
        ids = []
        for loot in self.allLoot:
            match = re.match(pattern, loot["lootId"])
            if match is not None:
                ids.append(int(match.group(1)))

        return ids
    
    def getLootByDisplayCategory(self, category):
        return [loot for loot in self.allLoot if loot["displayCategories"] == category]

    # refreshes loot (used after performing a task with loot)
    def refreshLoot(self):
        self.leagueConnection.post("/lol-loot/v1/refresh")
        sleep(1)
        self.allLoot = self.leagueConnection.get("/lol-loot/v1/player-loot").json()
        self.lastRefresh = time()


