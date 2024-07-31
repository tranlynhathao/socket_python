import socket
import threading
import json
import time
import os
import queue
import sys

q = queue.Queue()
endThread = queue.Queue()

def load_files():
    with open('files.json', 'r') as f:
        return json.load(f)

def waitForNewFile(client):
    while True:
        if not endThread.empty():
            break
        if q.empty():
            try:
                chunk = client.recv(13)
            except:
                continue
            while len(chunk) != 13:
                try:
                    chunkmini = client.recv(13 - len(chunk))
                except:
                    break
                chunk = chunk + chunkmini
            if chunk == b"NewFileDetect":
                chunk = ""
                q.put(1)
    return

def handle_client(client_socket, addr):
    try:
        files = load_files()
       
        files_list = "\n".join([f'{file["name"]} {file["size"]}MB' for file in files])
        client_socket.sendall(files_list.encode())
        while True:
            message = client_socket.recv(1024).decode()
            if message == "":
                print(f"{addr} disconnected !")
            if message[:13] == "NewFileDetect":
                continue
            fileName = []
            priority = []
            openedFile = []
            message = message.split("\n") 
            for temp in message:
                if temp == "":
                    break
                name, pri = temp.split(" ")
                fileName.append(name)
                priority.append(pri)
                print(f"Receive from {addr}:", name, pri)
            for file in fileName:
                openedFile.append(open(file, "rb"))
            for file in openedFile:
                file_size = os.fstat(file.fileno()).st_size
                temp = str(file_size)
                client_socket.sendall(temp.encode("utf-8"))
                client_socket.recv(3)
            detectFile = threading.Thread(target=waitForNewFile, args=(client_socket,))
            detectFile.start()
                
            while openedFile != []:
                newFile = ""
                for file, pri in zip(openedFile, priority):
                    if not q.empty():
                        newFile = client_socket.recv(1024).decode('utf-8')
                        data = b"NewFileIsComing"
                        while len(data) != 1024:
                            data = data + b"\0"
                        client_socket.sendall(data)
                        openNew = newFile.split("\n")
                        for filesss in openNew:
                            if filesss == "":
                                break
                            temp1, temp2 = filesss.split(" ")
                            priority.append(temp2)
                            openedFile.append(open(temp1, "rb"))
                            file_size = str(os.fstat(openedFile[-1].fileno()).st_size)
                            client_socket.sendall(file_size.encode("utf-8"))
                            client_socket.recv(3)
                            print(f"Add new file success {addr}: " + temp1,temp2)
                        foooo = q.get()
                    if pri == "CRITICAL":
                        i = 11
                    elif pri == "HIGH":
                        i = 5
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
                            openedFile.remove(file)
                            priority.remove(pri)
                            break
                        while len(chunk) != 1024:
                            chunk += b"\0"
                        client_socket.sendall(chunk)
                #printProgress
            print(f"Send complete for {addr}")
            endThread.put(1)
            detectFile.join()
            endThread.get()
    #except socket.error as e:
        #print(f"Client disconnected abruptly: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    host = socket.gethostbyname(socket.gethostname())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, 23127))
    server.listen(5)
    print(f"Server is listening on {host} 23127")

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
