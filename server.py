import socket # socket allows communication over a network
from _thread import * # thread lets the server have multple clients
import sys

# each client sends data to the server to proccess, server sends it back
# to all clients

server = "127.0.0.1" # server ip address (my computer)
port = 5555

# create a raw socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try: # try to bind the server to the server and port
    s.bind((server, port))
except socket.error as e: # error
    str(e)

# wait for connections, if we have at least 2 connections, we can start
s.listen(2)
print("Waiting for a connection, Server Started")

next_client_id = 1

def threaded_client(conn, client_id):
    conn.sendall(str.encode(str(client_id))) # send this client's unique ID
    reply = ""
    while True:
        try:
            data = conn.recv(2048) # server recieves 2048 bytes
            reply = data.decode("utf-8") # turn into text

            if not data: # no data being sent means we disconnected
                print("Disconnected")
                break
            else:
                print("Received: ", reply)
                print("Sending : ", reply)

            # sends all clients what the server recieved
            conn.sendall(str.encode(reply))
        except:
            break

    # closes disconnected clients
    print("Lost connection")
    conn.close()


while True:
    conn, addr = s.accept() # wait for client
    print("Connected to:", addr)
    client_id = next_client_id # set client id to be +1 from previous
    next_client_id += 1
    # start client thread
    start_new_thread(threaded_client, (conn, client_id))