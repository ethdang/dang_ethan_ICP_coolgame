import socket
from _thread import start_new_thread # get thread
from queue import Queue

class Network:
    def __init__(self):
        # creates socket that matches the one used by server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # sets server address
        self.server = "127.0.0.1" # to run server and main on same computer
        self.port = 5555
        self.addr = (self.server, self.port)
        self.messages = Queue()
        self.receive_buffer = ""

        # connect automatically to server
        self.id = self.connect()
        print(self.id)

        start_new_thread(self.listen, ()) # start thread that listens

    def connect(self):
        self.client.connect(self.addr) # connect the client to the server
        return int(self.receive_line())

    def send(self, data):
        try:
            self.client.sendall((data + "\n").encode())
        except socket.error as e: 
            print(e)

    def receive_line(self):
        while "\n" not in self.receive_buffer:
            self.receive_buffer += self.client.recv(2048).decode()
        line, self.receive_buffer = self.receive_buffer.split("\n", 1)
        return line

    def listen(self):
        while True:
            try:
                self.messages.put(self.receive_line())
            except socket.error:
                break

    def get_messages(self):
        messages = []
        while not self.messages.empty():
            messages.append(self.messages.get())
        return messages