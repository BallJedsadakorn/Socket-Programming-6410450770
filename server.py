import socket
import threading
import re

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5555

# Regular expression for command parsing
COMMAND_REGEX = r'^/(\w+)(?:\s(.*))?$'

# Dictionary to store nicknames of clients
clients_nickname = {}

# Function to handle client connections
def handle_client(client_socket, nickname):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message.startswith("/"):
                    handle_command(message, client_socket, nickname)
                else:
                    print(f"{nickname}: {message}")
                    broadcast_message(f"{nickname}: {message}")
            else:
                remove_client(client_socket, nickname)
                break
        except Exception as e:
            print(f"Error: {e}")
            remove_client(client_socket, nickname)
            break

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client in clients:
        client.send(message.encode("utf-8"))

# Function to handle commands
def handle_command(command, client_socket, nickname):
    if command.startswith("/list"):
        list_users(client_socket)
    elif command.startswith("/kick"):
        kick_user(command, client_socket)
    else:
        client_socket.send("Invalid command. Type /help for a list of available commands.".encode("utf-8"))

# Function to list all users
def list_users(client_socket):
    if clients:
        user_list = "Connected users:\n" + "\n".join(clients_nickname.values())
        client_socket.send(user_list.encode("utf-8"))
    else:
        client_socket.send("No users connected.".encode("utf-8"))

# Function to kick a user
def kick_user(command, client_socket):
    match = re.match(COMMAND_REGEX, command)
    if match:
        _, nickname_to_kick = match.groups()
        for client in clients:
            if clients_nickname[client] == nickname_to_kick:
                remove_client(client, nickname_to_kick)
                client_socket.send(f"{nickname_to_kick} has been kicked.".encode("utf-8"))
                return
        client_socket.send(f"User '{nickname_to_kick}' not found.".encode("utf-8"))

# Function to remove client from the list
def remove_client(client_socket, nickname):
    clients.remove(client_socket)
    print(f"{nickname} has left the chat.")
    broadcast_message(f"{nickname} has left the chat.")
    del clients_nickname[client_socket]
    client_socket.close()

# Main function to handle server operations
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server is listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")

        client_socket.send("Enter your nickname: ".encode("utf-8"))
        nickname = client_socket.recv(1024).decode("utf-8")
        clients.append(client_socket)
        clients_nickname[client_socket] = nickname

        print(f"User '{nickname}' has joined the chat.")
        broadcast_message(f"User '{nickname}' has joined the chat.")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, nickname))
        client_thread.start()

if __name__ == "__main__":
    clients = []
    main()
