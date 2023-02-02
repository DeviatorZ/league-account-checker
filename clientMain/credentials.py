import socket
import random
import string

def getFreePort(minPort=50000, maxPort=65000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for port in range(minPort, maxPort):
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            pass
    
    raise IOError("No available port")

def getAuthToken(length=22):   
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))