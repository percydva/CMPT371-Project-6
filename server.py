from copyreg import pickle
import socket
from _thread import *
import pickle
from game import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.1.69'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

players = [
            Player(0, 0, 50, 50, (255, 0 , 0)),
            Player(100, 100, 50, 50, (0, 0 , 255)), 
            Player(150, 150, 50, 50, (0, 0, 255)),
            Player(200, 200, 50, 50, (255, 0, 255))
          ]

def threaded_client(conn, player):
    conn.send(pickle.dumps(player)) # On initial connection
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data
            if not data:
                print("Connection lost.")
                break
            conn.sendall(pickle.dumps(players))
        except:
            break

    print("Connection Closed")
    conn.close()

currPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn, currPlayer))
    currPlayer += 1