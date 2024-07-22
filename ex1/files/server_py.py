import os
import socket

# Server configuration
host = socket.gethostbyname(socket.gethostname()) #"127.0.0.1" 
port = 23127
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
                    client_socket.sendall(data)

            client_socket.sendall(b"<EndOfFile>")
            print(f"Send complete for {file_name}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()














# from fileinput import filename
# import os
# import socket
# import threading

# # Server configuration
# host = "127.0.0.1"#socket.gethostbyname(socket.gethostname())
# port = 63353
# encoding = "utf-8"

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((host, port))
# server.listen()
# print("Server listen on:", host, port)

# def handle_client(client, addr):
#     with open("Read.txt", "r") as file:
#         message = file.read()
#         client.sendall(message.encode(encoding))
#     files = []
#     while True:
#         file = client.recv(32).decode(encoding)
#         if file == "ACK":
#             break
#         client.sendall(b"ACK")
#         files.append(file)
#     # for i in files:
#     #     print(i)
#     fileName =[]
#     pri =[]
#     for i in files:
#         i = i.split(" ")
#         fileName.append(i[0])
#         pri.append(i[1])
#     filecontent = []
#     for files in fileName:
#         with open(files, "rb") as file:
#             data = file.read()
#             filecontent.append(data)
#     # for i in filecontent:
#     #     print(len(i))
#     print(filecontent[3])    
#     client.close()

# while True:
#     client_socket, addr = server.accept()
#     print(f"Accepted connection from {addr}")
#     client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
#     client_handler.start()