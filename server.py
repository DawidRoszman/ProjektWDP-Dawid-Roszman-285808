import socket
from _thread import start_new_thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

currentId = "0"
pos = ["0:50,400,0", "1:900,400,0"]


def threaded_client(conn: socket):
    """create new thread for each client connection to server and send data to client and recieve data from client and send it to other client and close connection when client disconnects from server.

    Args:
        conn (socket): socket object of client connection
    """
    global currentId, pos
    if currentId == "0":
        conn.send(str.encode(currentId+";"+";".join(pos)))
    else:
        conn.send(str.encode(currentId+";"+";".join(pos[::-1])))
    currentId = "1"
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply
                nid = 0

                if id == 0:
                    nid = 1
                if id == 1:
                    nid = 0

                reply = pos[nid][:]
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
