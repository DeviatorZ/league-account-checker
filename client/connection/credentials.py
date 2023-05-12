import socket
import random
import string
from typing import Iterator

def getFreePorts(portCount: int = 100, minPort: int = 40000, maxPort: int = 65500) -> Iterator[int]:
    """
    Generator function to get free ports within a specified range.

    :paramportCount: The number of ports to yield.
    :param minPort: The minimum port number to start searching from.
    :maxPort: The maximum port number to search up to.

    Yields:
        int: A free port number.
    """
    portsGiven = 0
    
    for port in range(minPort, maxPort):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", port))
            sock.close()
            yield port
            portsGiven += 1
            if portsGiven >= portCount:
                return
        except OSError: # port taken
            pass

def getAuthToken(length: int = 22) -> str:
    """
    Generates a random authentication token.

    :param length: The length of the token to generate.

    :return: The generated authentication token.
    """  
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))