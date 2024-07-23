import socket
import threading
import json
import time

# Global variable to keep track of active clients
active_clients = {}

def load_files():
    with open('files.json', 'r') as f:
        return json.load(f)

def handle_client(client_socket, client_id):
    try:
        files = load_files()

        files_list = "\n".join([f'{file["name"]} {file["size"]}MB' for file in files])
        client_socket.sendall(files_list.encode())

        while True:
            requested_files = client_socket.recv(1024).decode().strip()
            if not requested_files:
                break

            requested_files = requested_files.split("\n")
            for requested_file in requested_files:
                if requested_file.strip():
                    filename, priority = requested_file.split()
                    priority = priority.upper()

                    chunk_size = 2048 if priority == "CRITICAL" else 1024 if priority == "HIGH" else 256 

                    try:
                        with open(filename, "rb") as f:
                            while chunk := f.read(chunk_size):
                                client_socket.sendall(chunk)
                    except FileNotFoundError:
                        print(f"File {filename} not found")
                        client_socket.sendall(f"Error: File {filename} not found".encode())

                    print(f"Completed downloading {filename}")

    except socket.error as e:
        print(f"Client {client_id} disconnected abruptly: {e}")
    except Exception as e:
        print(f"Error with client {client_id}: {e}")
    finally:
        client_socket.close()
        del active_clients[client_id]
        print(f"Client {client_id} socket closed. Active clients: {len(active_clients)}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 23127))
    server.listen(5)
    print("Server is listening on port 23127")

    client_id_counter = 1

    try:
        while True:
            client_socket, addr = server.accept()
            client_id = client_id_counter
            client_id_counter += 1

            # Add client to the active clients dictionary
            active_clients[client_id] = addr
            print(f"Accepted connection from {addr} with client ID {client_id}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
