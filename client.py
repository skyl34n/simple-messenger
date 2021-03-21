import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 40000

def server_connection(sock):
    while True:
        try:
            data = sock.recv(256)
        except:
            print("Connection with server closed...")
            os._exit(1)
        print(data.decode("utf-8"))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
    except:
        print("Couldn't connect to the server...")
    try:
        while True:
            action = input("Login/Register: ")
            if action.lower() == "register":
                username = input("Username: ")
                password = input("Password: ")
                s.send(f"register,{username},{password}".encode("utf-8"))
                response = s.recv(256).decode("utf-8")
                if response == "Registration completed":
                    print(response)
                elif response == "Account with that username already exists":
                    print(response)
                continue
            elif action.lower() == "login":
                username = input("Username: ")
                password = input("Password: ")
                s.send(f"login,{username},{password}".encode("utf-8"))
                response = s.recv(256).decode("utf-8")
                if response == f"Successfully logged in as {username}":
                    print(response)
                    break
                elif response == "Invalid credentials":
                    print(response)
                elif response == "Already logged in":
                    print(response)
                continue

        while True:
            peer = input("Who do you want to contact? ")
            s.send(f"peer_name,{peer}".encode("utf-8"))
            response = s.recv(256).decode("utf-8")
            if response== "Peer username not found":
                print(response)
                continue
            elif response == "Peer username found":
                print(response)
                break
        #kal
        peer_waiting_message = s.recv(256).decode("utf-8")
        print(peer_waiting_message)
        connection_message = s.recv(256).decode("utf-8")
        print(connection_message)

        thread = threading.Thread(target=server_connection, args=(s,), daemon=True)
        thread.start()
        while True:
            message = input()
            s.send(message.encode("utf-8"))
    except:
        print("Closing application...")