import socket
from _thread import start_new_thread
import sys
import time
import random

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server = sys.argv[1]
except Exception as ex:
    print(ex, "Using default server")
    server = '10.10.4.64'
server_ip = server
port = 6677
try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection", server_ip)


def generate_meteors():
    for i in range(15):
        x, y, r = [random.randint(100, 800),
                   random.randint(100, 700), random.randint(40, 60)]
        while any([abs(x-m[0]) < 100 and abs(y-m[1]) < 100 for m in meteors]):
            x, y, r = [random.randint(100, 800), random.randint(100, 700),
                       random.randint(40, 60)]
        meteors.append([x, y, r])


currentId = "0"
beginning_pos = ["0:50,400,0", "1:900,400,0"]
pos = beginning_pos[:]
bullets = ["", ""]
score = [0, 0]
game_state = "waiting_for_players"
meteors = []
generate_meteors()
ready = [0, 0]



def threaded_client(conn):
    """create new thread for each client connection to server and send data to
    client and recieve data from client and send it to other client and close
    connection when client disconnects from server.

    Args:
        conn (socket): socket object of client connection
    """
    global currentId, pos, bullets, score, game_state, ready, meteors
    if currentId == "0":
        conn.send(str.encode(currentId+";"+";".join(pos)))
    else:
        conn.send(str.encode(currentId+";"+";".join(pos[::-1])))
    currentId = "1" if currentId == "0" else "0"
    reply = ''
    while True:
        try:
            data = conn.recv(1024)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                if id in [0, 1]:
                    pos[id] = reply
                    nid = id

                    if id == 0:
                        nid = 1
                    if id == 1:
                        nid = 0

                    reply = pos[nid][:]
                elif id == 2:
                    print(bullets)
                    bullets[int(arr[1])] = arr[2]
                    reply = bullets[0]+":"+bullets[1]
                elif id == 3:
                    if arr[1] == 'hit':
                        score[int(arr[2])] += 1
                        game_state = "game_over"
                        if score[int(arr[2])] == 5:
                            game_state = "game_over_winner"
                    if currentId == "1":
                        game_state = "waiting_for_players"
                    if currentId == "0" and \
                                    game_state == "waiting_for_players":
                        game_state = "game"
                    reply = game_state

                elif id == 4:
                    print("Score:", score[0], score[1])
                    reply = str(score[0])+":"+str(score[1])
                elif id == 5:
                    reply = ":".join([str(m[0])+","+str(
                       m[1])+","+str(m[2]) for m in meteors])
                elif id == 6:
                    ready[int(arr[1])] = int(arr[2])
                    if ready[0] == 1 and ready[1] == 1:
                        print("game")
                        game_state = "game"
                        ready = [0, 0]
                        bullets = ["", ""]
                        print("Beginning pos:", beginning_pos)
                        pos = beginning_pos[:]
                        meteors = []
                        generate_meteors()
                    reply = str(ready[0])+":"+str(ready[1])

                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except Exception as ex:
            print(ex)
            break

    currentId = "1" if currentId == "0" else "0"
    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
