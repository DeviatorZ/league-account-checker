from time import sleep
from client.connection.LeagueConnection import LeagueConnection


def removeLeaverBusterNotifications(leagueConnection: LeagueConnection) -> None:
    notifications = leagueConnection.get("/lol-leaver-buster/v1/notifications").json()
    for notification in notifications:
        leagueConnection.delete(f"/lol-leaver-buster/v1/notifications/{notification['id']}")


def canQueueUp(leagueConnection: LeagueConnection, queueId: int, timeout: int = 15):
    eligibility = leagueConnection.post("/lol-lobby/v2/eligibility/party").json()
    for queueType in eligibility:
        if queueType["queueId"] == queueId:
            if queueType["eligible"]:
                return True
            elif queueType["restrictions"][0]["restrictionCode"] == "GameVersionMissing":
                for _ in range(timeout):
                    sleep(1)
                    clientState = leagueConnection.get("/lol-patch/v1/products/league_of_legends/state").json()
                    if clientState.get("action") == "Idle":
                        sleep(1)
                        return True
                return False
            else:
                return False
