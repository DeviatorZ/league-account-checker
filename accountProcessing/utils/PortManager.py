from accountProcessing.utils.PortHandler import PortHandler


class Ports:

    def __init__(self, riotPort: int, leaguePort: int) -> None:
        self.__riotPort = riotPort
        self.__leaguePort = leaguePort

    def getRiotPort(self) -> int:
        return self.__riotPort

    def getLeaguePort(self) -> int:
        return self.__leaguePort


class PortManager:

    def __init__(self, portHandler: PortHandler) -> None:
        self.__portHandler = portHandler
        self.__ports = None

    def __enter__(self) -> Ports:
        self.__ports = Ports(self.__portHandler.getFreePort(), self.__portHandler.getFreePort())
        return self.__ports

    def __exit__(self, *args, **kwargs) -> None:
        self.__portHandler.returnPort(self.__ports.getRiotPort())
        self.__portHandler.returnPort(self.__ports.getLeaguePort())
