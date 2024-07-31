import socket
import threading
from cryptography.fernet import Fernet

# Generate a new key (this should be done only once and shared securely)
# You can use this key for the first connection only and then hide it
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Save the key to a file (optional, for reuse)
with open('secret.key', 'wb') as key_file:
    key_file.write(key)

# Load the key from a file
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# List of connected clients
clients = []

# Function to broadcast messages to all connected clients
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            client.send(message)

# Function to handle the client
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            decrypted_message = cipher_suite.decrypt(message).decode()
            print(f"Received: {decrypted_message}")
            broadcast(message, client)
        except:
            break
    client.close()

# Function to start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen()

    print("Server started, waiting for connections...")

    while True:
        client, address = server.accept()
        print(f"Connection established with {address}")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Function to start the client
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))

    def receive_messages():
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break
                decrypted_message = cipher_suite.decrypt(message).decode()
                print(f"Received: {decrypted_message}")
            except:
                break

    thread = threading.Thread(target=receive_messages)
    thread.start()

    while True:
        message = input("Enter message: ")
        encrypted_message = cipher_suite.encrypt(message.encode())
        client.send(encrypted_message)

if __name__ == "__main__":
    choice = input("Do you want to start the server or client? (server/client): ").strip().lower()

    if choice == "server":
        start_server()
    elif choice == "client":
        start_client()
    else:
        print("Invalid choice. Exiting.")
