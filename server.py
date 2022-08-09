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

s.listen(4)
print("Waiting for a connection")

players = [Player(50, 50, 50, 50, (255, 0 , 0)), 
        Player(100, 100, 50, 50, (0, 255 , 0)),
        Player(0, 0, 50, 50, (0, 0 , 255)),
        Player(0, 50, 50, 50, (0, 0 , 0))]
def threaded_client(conn, player):
    # global currentId, pos
    conn.send(pickle.dumps(players[player]))
    reply1 = ''
    reply2 = ''
    reply3 = ''
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            # print('data:',data)
            # reply = data.decode('utf-8')
            players[player] = data
            if not data:
                print('Disconnected')
                break
            else:
                print("Recieved: ", data)

                if player == 0: 
                    reply1 = players[1]
                    reply2 = players[2]
                    reply3 = players[3]
                if player == 1: 
                    reply1 = players[0] 
                    reply2 = players[2]
                    reply3 = players[3]
                if player == 2: 
                    reply1 = players[0] 
                    reply2 = players[1]
                    reply3 = players[3]
                else:
                    reply1 = players[0]
                    reply2 = players[1]
                    reply3 = players[2]
                # print(reply)
                # reply = pos[nid][:]
                print("Sending: ", [reply1, reply2, reply3])

            conn.sendall(pickle.dumps([reply1, reply2, reply3]))
            # conn.sendall(pickle.dumps(reply2))
            # conn.sendall(pickle.dumps(reply3))
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