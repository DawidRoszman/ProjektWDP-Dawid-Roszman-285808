import socket


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.msg = self.connect().split(";")
        self.id = self.msg[0]
        self.posPlayer = self.msg[1].split(":")[1].split(",")
        self.posEnemy = self.msg[2].split(":")[1].split(",")
        print(self.posPlayer, self.posEnemy)

    def connect(self):
        """ Connect to server and return data from server

        Returns:
            str: decoded data from server 
        """
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()

    def send(self, data):
        """Send data to server and return reply from server

        Args:
            data (str): data to send to server

        Returns:
            str: reply from server
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
