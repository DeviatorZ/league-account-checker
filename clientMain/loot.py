from time import time
from time import sleep
import re

class Loot():
    def __init__(self, leagueConnection, refreshCooldown=5):
        self.leagueConnection = leagueConnection
        self.lastRefresh = 0
        self.refreshCooldown = refreshCooldown
        self.allLoot = self.leagueConnection.get("/lol-loot/v1/player-loot").json()

    def getLoot(self):
        return self.allLoot

    def getLootById(self, lootId):
        for loot in self.allLoot:
            if loot["lootId"] == lootId:
                return loot

    def getShardIdsByPattern(self, pattern):
        ids = []
        for loot in self.allLoot:
            match = re.match(pattern, loot["lootId"])
            if match is not None:
                ids.append(int(match.group(1)))

        return ids

    def refreshLoot(self):
        try:
            sleep(self.refreshCooldown - time() + self.lastRefresh)
        except Exception:
            pass

        self.leagueConnection.post("/lol-loot/v1/refresh")
        self.allLoot = self.leagueConnection.get("/lol-loot/v1/player-loot").json()     
        self.lastRefresh = time()


