from typing import List, Deque
from multiprocessing import Lock


class PortHandler:

    def __init__(self, ports: Deque, portsInUse: List, lock: Lock) -> None:
        self.__lock = lock
        self.__ports = ports
        self.__portsInUse = portsInUse

    def getFreePort(self) -> int:
        with self.__lock:
            freePort = self.__ports.pop()
            self.__portsInUse.append(freePort)
            return freePort

    def returnPort(self, port: int) -> None:
        with self.__lock:
            self.__ports.append(port)
            self.__portsInUse.remove(port)
