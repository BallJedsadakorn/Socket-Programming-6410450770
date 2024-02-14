import socket
import threading

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5555

# Function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
        except Exception as e:
            print(f"Error: {e}")
            break

# Main function to handle client operations
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"Error: {e}")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        try:
            message = input()
            client_socket.send(message.encode("utf-8"))
        except KeyboardInterrupt:
            print("Exiting...")
            client_socket.close()
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
