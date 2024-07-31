import os
import socket

# Server configuration
host = socket.gethostbyname(socket.gethostname()) #"127.0.0.1" 
port = 23126
encoding = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

while True:
    server.listen()
    print(f"Server running on {host}:{port}")
    print("Waiting for client...")
    client_socket, client_addr = server.accept()
    print(f"Connected to {client_addr}")
    try:
        with open("Read.txt", "r") as file:
            data = file.read()
            client_socket.sendall(data.encode(encoding))
        while True:
            message = client_socket.recv(1024).decode(encoding)
            
            if (message == ''):
                print(f"{client_addr} disconnected")
                break
            print(f"Received from client: {message}")
            file_name = f"{message}"
            
            size = os.path.getsize(file_name)
            
            client_socket.sendall(str(size).encode(encoding))

            with open(file_name, "rb") as file:
                while (data := file.read(1024)):
                    while len(data) != 1024:
                        data = data + b'\0'
                    client_socket.sendall(data)
                    
            temp = b"<EndOfFile>"
            while len(temp := temp + b'\0') != 1024:
                continue
            client_socket.sendall(temp)
            print(f"Send complete for {file_name}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()