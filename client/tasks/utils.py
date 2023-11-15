from time import sleep
from client.connection.LeagueConnection import LeagueConnection
from client.tasks.exceptions import LobbyException


def removeLeaverBusterNotifications(leagueConnection: LeagueConnection) -> None:
    notifications = leagueConnection.get("/lol-leaver-buster/v1/notifications").json()
    for notification in notifications:
        leagueConnection.delete(f"/lol-leaver-buster/v1/notifications/{notification['id']}")


def canQueueUp(leagueConnection: LeagueConnection, queueId: int):
    leagueConnection.waitForUpdate()
    eligibility = leagueConnection.post("/lol-lobby/v2/eligibility/party").json()
    for queueType in eligibility:
        if queueType["queueId"] == queueId:
            if queueType["eligible"]:
                return True
            elif queueType["restrictions"][0]["restrictionCode"] == "GameVersionMissing":
                raise LobbyException("canQueueUp check failed: GameVersionMissing")
            else:
                return False

    raise LobbyException(f"canQueueUp check failed: queueId-{queueId} not found")
