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

# Status codes and phrases
STATUS_OK = 200, "OK"
STATUS_BAD_REQUEST = 400, "Bad Request"
STATUS_NOT_FOUND = 404, "Not Found"
STATUS_INTERNAL_ERROR = 500, "Internal Server Error"


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
        response = create_http_response_ok(message)
        client.send(response.encode("utf-8"))

# Function to create HTTP response
def create_http_response_ok(content):
    status_line = f"HTTP/1.1 {STATUS_OK} \r\n"
    headers = "Content-Type: text/plain\r\n"
    body = f"\r\n{content}"
    return status_line + headers + body

def create_http_response_bad(content):
    status_line = f"HTTP/1.1 {STATUS_BAD_REQUEST} \r\n"
    headers = "Content-Type: text/plain\r\n"
    body = f"\r\n{content}"
    return status_line + headers + body
    
def create_http_response_bad_NOT_FOUND(content):
    status_line = f"HTTP/1.1 {STATUS_NOT_FOUND} \r\n"
    headers = "Content-Type: text/plain\r\n"
    body = f"\r\n{content}"
    return status_line + headers + body

def create_http_response_STATUS_INTERNAL_ERROR(content):
    status_line = f"HTTP/1.1 {STATUS_INTERNAL_ERROR} \r\n"
    headers = "Content-Type: text/plain\r\n"
    body = f"\r\n{content}"
    return status_line + headers + body


# Function to handle commands
def handle_command(command, client_socket, nickname):
    if command.startswith("/list"):
        list_users(client_socket)
    elif command.startswith("/kick"):
        kick_user(command, client_socket)
    else:
        send_status_bad(client_socket, STATUS_BAD_REQUEST, "Invalid command.")

# Function to list all users
def list_users(client_socket):
    if clients:
        user_list = "Connected users:\n" + "\n".join(clients_nickname.values())
        response = create_http_response_ok(user_list)
        client_socket.send(response.encode("utf-8"))
    else:
        send_status_not(client_socket, STATUS_NOT_FOUND, "No users connected.")

# Function to kick a user
def kick_user(command, client_socket):
    match = re.match(COMMAND_REGEX, command)
    if match:
        _, nickname_to_kick = match.groups()
        for client in clients:
            if clients_nickname[client] == nickname_to_kick:
                remove_client(client, nickname_to_kick)
                send_status_ok(client_socket, STATUS_OK, f"{nickname_to_kick} has been kicked.")
                return
        send_status_not(client_socket, STATUS_NOT_FOUND, f"User '{nickname_to_kick}' not found.")
    else:
        send_status_in(client_socket, STATUS_BAD_REQUEST, "Invalid kick command format.")

# Function to send status messages
def send_status_ok(client_socket, status_code, message):
    response = create_http_response_ok(message)
    client_socket.send(response.encode("utf-8"))

def send_status_bad(client_socket, status_code, message):
    response = create_http_response_bad(message)
    client_socket.send(response.encode("utf-8"))

def send_status_not(client_socket, status_code, message):
    response = create_http_response_bad_NOT_FOUND(message)
    client_socket.send(response.encode("utf-8"))

def send_status_in(client_socket, status_code, message):
    response = create_http_response_STATUS_INTERNAL_ERROR(message)
    client_socket.send(response.encode("utf-8"))

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
        broadcast_message(f"User '{nickname}' joined the chat.")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, nickname))
        client_thread.start()

if __name__ == "__main__":
    clients = []
    main()
