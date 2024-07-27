import socket
import threading
import json
import time
import os

def load_files():
    with open('files.json', 'r') as f:
        return json.load(f)

def handle_client(client_socket, addr):
    try:
        files = load_files()

        files_list = "\n".join([f'{file["name"]} {file["size"]}MB' for file in files])
        client_socket.sendall(files_list.encode())
        while True:
            requested_files = client_socket.recv(1024).decode()
            if requested_files == "":
                print(f'{addr} disconnected')
                break
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
            print(f"Send complete for {addr}")            
        
    except socket.error as e:
        print(f"Client disconnected abruptly: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    host = socket.gethostbyname(socket.gethostname())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, 23127))
    server.listen(5)
    print(f"Server is listening on {host} port 23127")

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