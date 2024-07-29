import queue
import socket
import threading
import time
import sys
import os
import signal

code = "utf-8"

# Signal handler to exit program

q = queue.Queue()
openedFile = []
file_sizes = {}
fileName = []
filepri = []

def signal_handler(sig, frame):
    print('\nExiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_progress_all(downloaded_sizes, file_sizes):
    sys.stdout.write("\033c")  # Clear screen
    for file_name in downloaded_sizes:
        progress_percentage = (float(downloaded_sizes[file_name]) / file_sizes[file_name]) * 100
        print(f"Downloading {file_name} .... {progress_percentage:.2f}%\n")
    time.sleep(0.0001)

def downloadFiles(client, fileNamee, filepri, message):
    q.put(1)
    client.sendall(message.encode(code))
    for file in fileNamee:
        openedFile.append(open(file, "wb"))
    
    for file in fileNamee:
        data = client.recv(50).decode(code)
        client.sendall(b"ACK")
        file_sizes[file] = int(data)
        # print(file + " ")
        # print(data)
        # print("\n")

    #file_sizes[file] = file_size
    
    downloaded_sizes = {file: 0 for file in fileNamee}

    while fileNamee != []:
        for file, pri, name in zip(openedFile, filepri, fileNamee):
            if pri == "CRITICAL":
                i = 11
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[:15] == b"NewFileIsComing":
                        for newName in fileName:
                            if not os.path.exists(newName):
                                openedFile.append(open(newName, 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(1024).decode(code)
                                file_sizes[newName] = int(sizeNew)
                                client.sendall(b"ACK")
                        chunk = None
                        chunk = client.recv(1024)
                        while len(chunk) != 1024:
                            chunkmini = client.recv(1024 - len(chunk))
                            chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        openedFile.remove(file)
                        filepri.remove(pri)
                        fileName.remove(name)
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
            elif pri == "HIGH":
                i = 5
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[:15] == b"NewFileIsComing":
                        for newName in fileName:
                            if not os.path.exists(newName):
                                openedFile.append(open(newName, 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(50).decode(code)
                                client.sendall(b"ACK")
                                file_sizes[newName] = int(sizeNew)
                        chunk = None
                        chunk = client.recv(1024)
                        while len(chunk) != 1024:
                            chunkmini = client.recv(1024 - len(chunk))
                            chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        openedFile.remove(file)
                        filepri.remove(pri)
                        fileName.remove(name)
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
            else :
                i = 2
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[:15] == b"NewFileIsComing":
                        for newName in fileName:
                            if not os.path.exists(newName):
                                openedFile.append(open(newName, 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(50).decode(code)
                                client.sendall(b"ACK")
                                file_sizes[newName] = int(sizeNew)
                        chunk = None
                        chunk = client.recv(1024)
                        while len(chunk) != 1024:
                            chunkmini = client.recv(1024 - len(chunk))
                            chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        openedFile.remove(file)
                        filepri.remove(pri)
                        fileName.remove(name)
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
        #printProgress
        
        print_progress_all(downloaded_sizes, file_sizes)
    q.get()
    print("Complete downloading")
    client.sendall(b"close__thread")

def main():
    server_address = ('192.168.1.17', 23127)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        files_list = client_socket.recv(1024).decode()
        print("Files available for download:\n" + files_list)
        check = True
        while True:
            with open("input.txt", "r") as f:
                requested_files = f.read()
            requested_files = requested_files.split("\n") 
            key = 0
            message = ""
            for file in requested_files:
                name, pri = file.split(" ")
                if os.path.exists(name) == True:
                    continue
                key = 1
                fileName.append(name)
                filepri.append(pri)
                message = message + name + " " + pri + "\n"
            # print(fileName)
            # print(len(numberOfThread))
            # print(numberOfThread)
                
            if fileName != [] and q.empty() and key == 1:
                key = 0
                check = False
                downloadThread = threading.Thread(target=downloadFiles, args=(client_socket, fileName, filepri, message))
                downloadThread.start()
            elif fileName != [] and not q.empty() and key == 1:
                key = 0
                client_socket.sendall(b"NewFileDetect")
                client_socket.sendall(message.encode(code))
            time.sleep(2)
            #print("\nWait 2 seconds to read input again")

        
        
    except KeyboardInterrupt:
        print("\nClient is shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()