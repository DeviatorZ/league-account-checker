from time import time
from time import sleep

class Loot():
    def __init__(self, leagueConnection, refreshCooldown=5):
        self.leagueConnection = leagueConnection
        self.lastRefresh = 0
        self.refreshCooldown = refreshCooldown

    def getLoot(self):
        return self.leagueConnection.get("/lol-loot/v1/player-loot").json()

    def getLootById(self, lootId):
        return self.leagueConnection.get(f"/lol-loot/v1/player-loot/{lootId}").json()

    def refreshLoot(self):
        try:
            sleep(self.refreshCooldown - time() + self.lastRefresh)
        except Exception:
            pass

        self.leagueConnection.post("/lol-loot/v1/refresh")     
        self.lastRefresh = time()


