import socket
import time
import threading
import json

HOST = "127.0.0.1"
PORT = 40000

client_sockets = {}
user_pairs = {}  # {(user_socket, username): peer_name}

def connect_client(client_socket, client_address):
    print(f"[{time.strftime('%H:%M:%S')}] Connection with {client_address} has been established")
    with client_socket:
        try:
            while True:
                initial_packet = client_socket.recv(256).decode("utf-8")
                initital_packet_data = initial_packet.split(",")
                action = initital_packet_data[0]
                username = initital_packet_data[1]
                password = initital_packet_data[2]
                with open("accounts.json", "r+") as file:
                    accounts = json.load(file)
                    if action == "register":
                        if not username in accounts:
                            accounts[username] = password
                            client_socket.send("Registration completed".encode("utf-8"))
                            continue
                        else:
                            client_socket.send("Account with that username already exists".encode("utf-8"))
                            continue
                    elif action == "login":
                        if username in accounts:
                            if username in client_sockets:
                                client_socket.send("Already logged in".encode("utf-8"))
                                continue
                            if password != accounts[username]:
                                client_socket.send("Invalid credentials".encode("utf-8"))
                                continue
                            client_socket.send(f"Successfully logged in as {username}".encode("utf-8"))
                            break
                        else:
                            client_socket.send("Invalid credentials".encode("utf-8"))
                            continue
            client_sockets[username] = client_socket
        except:
            print(f"[{time.strftime('%H:%M:%S')}] Closing connection with {client_address[0]}:{client_address[1]}...")
            del client_sockets[username]

        try:
            while True:
                peer_name_message = client_socket.recv(256).decode("utf-8").split(",")
                peer_name = peer_name_message[1]
                with open("accounts.json", "r+") as file:
                    accounts = json.load(file)
                    if peer_name not in accounts:
                        client_socket.send("Peer username not found".encode("utf-8"))
                        continue
                    client_socket.send("Peer username found".encode("utf-8"))
                    user_pairs[(client_socket, username)] = peer_name
                    client_socket.send("Waiting for your peer...".encode("utf-8"))
                    break
        except:
            print(f"[{time.strftime('%H:%M:%S')}] Closing connection with {client_address[0]}:{client_address[1]}...")
            del client_sockets[username]

        try:
            connection_established = False
            while not connection_established:
                for key in user_pairs.copy():
                    if username == user_pairs[key]:
                        peer_socket = key[0]
                        client_socket.send("Connection established!".encode("utf-8")) # kal
                        connection_established = True
                        break
        except:
            print(f"[{time.strftime('%H:%M:%S')}] Closing connection with {client_address[0]}:{client_address[1]}...")
            del client_sockets[username]

        try:
            while True:
                    data = client_socket.recv(256)  
                    peer_socket.send(f"[{username}]: {data.decode('utf-8')}".encode("utf-8"))
                    print(f"[{username}]: {data.decode('utf-8')}")
        except:
            print(f"[{time.strftime('%H:%M:%S')}] Closing connection with {client_address[0]}:{client_address[1]}...")
            del client_sockets[username]
            if (client_socket, username) in user_pairs:
                del user_pairs[(client_socket, username)]
            for key, value in user_pairs.items():
                if value == username:
                    _peer_socket = key[0]
                    _peer_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[{time.strftime('%H:%M:%S')}] Server started, waiting for incoming connections...\n")
    while True:
        client_socket, client_address = s.accept()
        threading.Thread(target=connect_client, args=(client_socket, client_address)).start()
