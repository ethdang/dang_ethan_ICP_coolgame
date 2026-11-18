import socket # socket allows communication over a network
from _thread import * # thread lets the server have multple clients
import sys

'''
    Server recieves messages from client and broadcasts to other clients

    Client sends input/event
            ↓
    Server validates and updates game_state
            ↓
    Server broadcasts the updated result
            ↓
    Clients update their local display
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
player_data = {}

game_state = {
    "phase": "waiting",  # waiting, playing, finished
    "level": 1,
    "players": {},
    "walls": [],
    "collected_coins": []
}

def threaded_client(conn, client_id): # client id is the client who sent
    while True:
        try:
            data = conn.recv(2048) # recieve data, maximum amt of byte 2048
            if not data: # did not recieve, client most likely disconnected
                print("Disconnected") 
                break
            for message in data.decode("utf-8").splitlines(): 
                parts = message.split(":")
                # handle some messages to store in server

                # check for client_id because we store data by the id
                # player is ready

                if not int(parts[1]) == client_id:
                    return

                match parts[0]:
                    case "ready":
                        game_state["players"][client_id]["ready"] = True
                        broadcast(f"player_ready:{client_id}", exclude=conn)

                        readied = 0 
                        for player in game_state["players"].values(): # check if all players are ready
                            if player["ready"]:
                                readied += 1

                        if readied == len(game_state["players"]): 
                            game_state["phase"] = "selection"
                            broadcast("selection_finished")

                        continue # skip other broadcast message
                    # player finished course
                    case "finished":
                        finish_time = float(parts[2])

                        game_state["players"][client_id]["finished"] = True
                        game_state["players"][client_id]["finish_time"] = finish_time

                        broadcast(f"player_finished:{client_id}:{finish_time}", exclude=conn)

                        finished = 0 
                        fastest_time = 0
                        fastest_player = 0
                        for player in game_state["players"].values(): # check all players
                            if player["finish_time"]: # if we have a finish time, we finished 
                                finished += 1
                                
                                if not fastest_time: # if we dont have a fastest time yet,
                                    fastest_time = player["finish_time"]
                                    fastest_player = player
                                    continue

                                if fastest_time > player["finish_time"]: # if the fastest time is slower
                                    fastest_time = player["finish_time"] # set new fastest
                                    fastest_player = player

                                player["score"] += 1 # 1 point for finishing

                        fastest_player["score"] += 1 # another point for finishing first

                        # check how many players have finished
                        if finished == len(game_state["players"]):
                            print("all player finished")
                            game_state["phase"] = "round_finished" # set phase
                            broadcast("all_player_finished")

                            for player_id, player in game_state["players"].items(): # items() gets item in dict
                                # send the scores for each player
                                broadcast(f"updated_score:{player_id}:{player['score']}")
                                broadcast(f"player_status:{player_id}:{"finished"}")
                        
                        continue # skip other broadcast message

                    case "placed":
                        game_state["players"][client_id]["has_placed"] = True
                        broadcast(f"player_status:{client_id}:{"finished_placement"}")

                        done_placed = 0
                        for player in game_state["players"].values(): # check if all players are ready
                            if player["has_placed"]:
                                done_placed += 1

                        if done_placed == len(game_state["players"]): 
                            game_state["phase"] = "playing"
                            broadcast("finished_placement")

                        # dont continue because we still want the wall to be placed

            broadcast(message, exclude=conn) # broadcast data to excluding the sender
        except Exception as error:
            print(f"Client {client_id} error:", error)
            break
    # remove data for the client that disconnected
    if client_id in game_state["players"]:
        del game_state["players"][client_id]

    print(f"{client_id} lost connection")

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
    # add empty player data to new player
    game_state["players"][client_id] = {
        "ready": False,
        "finished": False,
        "finish_time": None,
        "score" : 0,
        "has_placed": False # has the player placed their object yet
    }

    conn.sendall((str(client_id) + "\n").encode())
    for existing_client_id in range(1, client_id):
        conn.sendall((f"player_joined:{existing_client_id}\n").encode())
        conn.sendall((f"player_status:{client_id}:{" "}\n").encode())
    broadcast(f"player_joined:{client_id}")
    broadcast(f"player_status:{client_id}:{" "}")

    # start client thread
    start_new_thread(threaded_client, (conn, client_id))