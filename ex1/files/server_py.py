import os
import socket
import threading


# Server configuration


host = "127.0.0.1"
port = 63353
encoding = "utf-8"

def handle_client(client_socket, client_addr):
    print(f"Connected to {client_addr}")
    try:
        with open("./Read.txt", "r") as file:
            data = file.read()
            client_socket.sendall(data.encode(encoding))
        
        while True:
            try:
                message = client_socket.recv(512).decode(encoding)
            except:
                break
            if not message:
                print(f"Received from client {client_addr}: null")
                break
            
            print(f"Received from client {client_addr}: {message}")
            file_name = f"File{message}.zip"
            if not os.path.exists(file_name):
                client_socket.sendall(b"File not found")
                continue
            
            size = os.path.getsize(file_name)
            client_socket.sendall(str(size).encode(encoding))

            with open(file_name, "rb") as file:
                while (data := file.read(1024)):
                    client_socket.sendall(data)
                    if client_socket.recv(3) != b"ACK":
                        print("Error: ACK not received")

            client_socket.sendall(b"<ENDGAMEEHAHAHA>")
            print(f"Send complete for {file_name} to {client_addr}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind((host, port))
    server.listen()  
    
    print(f"Server running on {host}:{port}")

    while True:
        print("Waiting for client...")
        client_socket, client_addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_handler.start()

if __name__ == "__main__":
    main()
