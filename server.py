import socket
from _thread import start_new_thread
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555
try:
    server_ip = sys.argv[1]
except Exception:
    server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection", server_ip)

currentId = "0"
beginning_pos = ["0:50,400,0", "1:900,400,0"]
pos = beginning_pos[:]
bullets = ["", ""]
score = [0, 0]


def threaded_client(conn):
    """create new thread for each client connection to server and send data to
    client and recieve data from client and send it to other client and close
    connection when client disconnects from server.

    Args:
        conn (socket): socket object of client connection
    """
    global currentId, pos, bullets, score
    if currentId == "0":
        conn.send(str.encode(currentId+";"+";".join(pos)))
    else:
        conn.send(str.encode(currentId+";"+";".join(pos[::-1])))
    currentId = "1" if currentId == "0" else "0"
    reply = ''
    while True:
        try:
            data = conn.recv(3048)
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
                    print("Player", arr[1], "lost")
                    pos = beginning_pos[:]
                elif id == 4:
                    score[int(arr[1])] = int(arr[2])
                    print("Score:", score[0], score[1])
                    reply = str(score[0])+":"+str(score[1])

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
