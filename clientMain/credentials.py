import socket
import random
import string

# finds a free port 
def getFreePort(minPort=50000, maxPort=65000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for port in range(minPort, maxPort):
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError: # port taken
            pass
    
    raise IOError("No available port")

# generates a random string that's used as a league/riot client auth token
def getAuthToken(length=22):   
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))