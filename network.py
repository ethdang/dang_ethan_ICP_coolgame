import socket

class Network:
    def __init__(self):
        # creates socket that matches the one used by server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # sets server address
        self.server = "127.0.0.1" # to run server and main on same computer
        self.port = 5555
        self.addr = (self.server, self.port)

        # connect automatically to server
        self.id = self.connect()
        print(self.id)

    def connect(self):
        try: # if we connected, set our id
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except: # try to connect, if we cannot, pass
            pass

    def send(self, data):
        try:
            # convert text to byte, send to server, 
            # wait for response, convert response to text, 
            # return the text

            self.client.send(str.encode(data))
            return self.client.recv(2048).decode()
        except socket.error as e: 
            # would be an error because we shouldnt be able to send if we are not connected
            print(e)