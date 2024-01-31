from time import sleep
from client.connection.LeagueConnection import LeagueConnection
from typing import Optional, Tuple


def removeLeaverBusterNotifications(leagueConnection: LeagueConnection) -> None:
    notifications = leagueConnection.get("/lol-leaver-buster/v1/notifications").json()
    for notification in notifications:
        leagueConnection.delete(f"/lol-leaver-buster/v1/notifications/{notification['id']}")


def __getCanQueueState(leagueConnection: LeagueConnection, queueId: int) -> Tuple[bool, Optional[str]]:
    eligibility = leagueConnection.post("/lol-lobby/v2/eligibility/party").json()
    for queueType in eligibility:
        if queueType["queueId"] == queueId:
            if queueType["eligible"]:
                return True, None
            elif queueType["restrictions"]:
                return False, queueType["restrictions"][0]["restrictionCode"]
            else:
                return False, "Unknown error"

    return False, f"queueId-{queueId} not found"


def canQueueUp(leagueConnection: LeagueConnection, queueId: int, retryLimit: int = 15, retryCooldown: int = 2) -> Tuple[bool, Optional[str]]:
    leagueConnection.waitForUpdate()

    for retryIndex in range(1, retryLimit + 1):
        canQueue, error = __getCanQueueState(leagueConnection, queueId)
        if canQueue or error == "QueueDisabled":
            return canQueue, error

        sleep(retryCooldown if retryIndex < retryLimit else 0)

    return canQueue, error
