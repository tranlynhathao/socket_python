import socket
import threading
import json
import time
import os

def custom_length(b):
    count = 0
    for byte in b:
        if byte == 0:
            break
        count += 1       
    return count

def load_files():
    with open('files.json', 'r') as f:
        return json.load(f)

def handle_client(client_socket, addr):
    try:
        files = load_files()

        files_list = "\n".join([f'{file["name"]} {file["size"]}MB' for file in files])
        client_socket.sendall(files_list.encode())

        requested_files = client_socket.recv(1024).decode()
        requested_files = requested_files.split("\n") 
        fileName = []
        priority = []
        for file in requested_files:
            if file == "":
                continue
            name, pri = file.split(" ")
            fileName.append(name)
            priority.append(pri)
            print(f"Receive from {addr}:", name, pri)
        listFile = []
        for file in fileName:
            listFile.append(open(file, "rb"))
        
        for file in listFile:
            file_size = os.fstat(file.fileno()).st_size
            temp = str(file_size)
            client_socket.sendall(temp.encode("utf-8"))
            client_socket.recv(3)

        while listFile != []:
            for file, pri in zip(listFile, priority):
                if pri == "CRITICAL":
                    i = 11
                    while i := i - 1:
                        chunk = file.read(1024)
                        if chunk == b"":
                            chunk = b"end_of_this_file"
                            while len(chunk := chunk + b"\0") != 1024:
                                continue
                            client_socket.sendall(chunk)
                            file.close()
                            listFile.remove(file)
                            priority.remove(pri)
                            break
                        while len(chunk) != 1024:
                            chunk += b"\0"
                        client_socket.sendall(chunk)
                elif pri == "HIGH":
                    i = 5
                    while i := i - 1:
                        chunk = file.read(1024)
                        if chunk == b"":
                            chunk = b"end_of_this_file"
                            while len(chunk := chunk + b"\0") != 1024:
                                continue
                            client_socket.sendall(chunk)
                            file.close()
                            listFile.remove(file)
                            priority.remove(pri)
                            break
                        while len(chunk) != 1024:
                            chunk += b"\0"
                        client_socket.sendall(chunk)
                else:
                    i = 2
                    while i := i - 1:
                        chunk = file.read(1024)
                        if chunk == b"":
                            chunk = b"end_of_this_file"
                            while len(chunk := chunk + b"\0") != 1024:
                                continue
                            client_socket.sendall(chunk)
                            file.close()
                            listFile.remove(file)
                            priority.remove(pri)
                            break
                        while len(chunk) != 1024:
                            chunk += b"\0"
                        client_socket.sendall(chunk)
            #printProgress
        print("Send complete")            
        
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
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()