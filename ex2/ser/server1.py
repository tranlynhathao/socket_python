# import os
# import socket

# # Server configuration
# host = socket.gethostbyname(socket.gethostname()) #"127.0.0.1" 
# port = 23127
# encoding = "utf-8"

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((host, port))

# while True:
#     server.listen()
#     print(f"Server running on {host}:{port}")
#     print("Waiting for client...")
#     client_socket, client_addr = server.accept()
#     print(f"Connected to {client_addr}")
#     try:
#         with open("Read.txt", "r") as file:
#             data = file.read()
#             client_socket.sendall(data.encode(encoding))
#         while True:
#             message = client_socket.recv(1024).decode(encoding)
            
#             if (message == ''):
#                 print(f"{client_addr} disconnected")
#                 break
#             print(f"Received from client: {message}")
#             file_name = f"{message}"
            
#             size = os.path.getsize(file_name)
            
#             client_socket.sendall(str(size).encode(encoding))

#             with open(file_name, "rb") as file:
#                 while (data := file.read(1024)):
#                     client_socket.sendall(data)

#             client_socket.sendall(b"<EndOfFile>")
#             print(f"Send complete for {file_name}")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()





import socket
import threading
import json
import time

def load_files():
    with open('files.json', 'r') as f:
        return json.load(f)

def handle_client(client_socket):
    try:
        files = load_files()

        files_list = "\n".join([f'{file["name"]} {file["size"]}MB' for file in files])
        client_socket.sendall(files_list.encode())

        requested_files = client_socket.recv(1024).decode().split("\n")
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
        print(f"Client disconnected abruptly: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 23127))
    server.listen(5)
    print("Server is listening on port 23127")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()