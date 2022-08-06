from copyreg import pickle
import socket
from _thread import *
import pickle
from game import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.1.71'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

players = [Player(0, 0, 50, 50, (255, 0 , 0)), Player(100, 100, 50, 50, (0, 0 , 255))]
def threaded_client(conn, player):
    # global currentId, pos
    conn.send(pickle.dumps(players[player]))
    reply = ''
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            # reply = data.decode('utf-8')
            players[player] = data
            if not data:
                print('Disconnected')
                break
            else:
                print("Recieved: ", data)

                if player == 0: reply = players[1]
                if player == 1: reply = players[0]

                # reply = pos[nid][:]
                print("Sending: ", reply)

            conn.sendall(pickle.dumps(reply))
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