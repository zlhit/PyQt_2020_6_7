import numpy as np
import pickle
import socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
serversocket.bind((ip, 5000))
serversocket.listen(1000)
clientsocket, clientaddress = serversocket.accept()

while 1:

    data = clientsocket.recv(1000).decode()
    print(data)