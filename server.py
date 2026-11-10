import socket # socket allows communication over a network
from _thread import * # thread lets the server have multple clients
import sys

'''
    Server recieves messages from client and broadcasts to other clients

'''
server = "127.0.0.1" # server ip address (my computer)
# server = "0.0.0.0" # run on same wifi
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
clients = []

def threaded_client(conn, client_id):
    while True:
        try:
            data = conn.recv(2048) # recieve data
            if not data: # did not recieve, server most likely disconnected
                print("Disconnected") 
                break
            for message in data.decode("utf-8").splitlines(): 
                # print("Received:", message)
                broadcast(message, exclude=conn) # broadcast data to excluding the sender
        except:
            break

    print("Lost connection")
    if conn in clients:
        clients.remove(conn) # remove clients
    conn.close() # close connection

def broadcast(message, exclude=None):
    for client in clients[:]:
        if client is exclude:
            continue # skip excluded clients (one who sent the data)
        try: # send data to all clients except excluded
            client.sendall((message + "\n").encode())
        except socket.error:
            clients.remove(client) # remove client if they cannot recieve

while True:
    conn, addr = s.accept() # wait for client
    print("Connected to:", addr)
    client_id = next_client_id # set client id to be +1 from previous
    next_client_id += 1

    clients.append(conn)

    conn.sendall((str(client_id) + "\n").encode())
    for existing_client_id in range(1, client_id):
        conn.sendall((f"player_joined:{existing_client_id}\n").encode())
    broadcast(f"player_joined:{client_id}")

    # start client thread
    start_new_thread(threaded_client, (conn, client_id))