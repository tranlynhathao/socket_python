import queue
import socket
import threading
import time
import sys
import os
import signal

code = "utf-8"
checking = queue.Queue()

def getFile(q, checking):
    while True:
        if not checking.empty():
            break
        with open("input.txt", "r") as f:
            inFile = f.read()
            q[0].put(inFile)
        if not checking.empty():
            break
        #print("\nWait 2 seconds to read input again")
        if not checking.empty():
            break
        time.sleep(2)

# Signal handler to exit program
def signal_handler(sig, frame):
    checking.put(1)
    sys.stdout.write("\033c")  # Clear screen
    print('Exiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_progress_all(downloaded_sizes, file_sizes):
    sys.stdout.write("\033c")  # Clear screen
    for file_name in downloaded_sizes:
        progress_percentage = (float(downloaded_sizes[file_name]) / file_sizes[file_name]) * 100
        print(f"Downloading {file_name} .... {progress_percentage:.2f}%\n")
    time.sleep(0.01)

def downloadFiles(client, listFileName, listPri, message):
    listFile = []
    client.sendall(message.encode(code))
    for file in listFileName:
        listFile.append(open(file, "wb"))
    
    file_sizes = {}
    for file in listFileName:
        data = client.recv(50).decode(code)
        client.sendall(b"ACK")
        file_sizes[file] = int(data)
        # print(file + " ")
        # print(data)
        # print("\n")

    #file_sizes[file] = file_size

    downloaded_sizes = {file: 0 for file in listFileName}

    while listFileName != []:
        for file, pri, name in zip(listFile, listPri, listFileName):
            if pri == "CRITICAL":
                i = 11
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        listFile.remove(file)
                        listPri.remove(pri)
                        listFileName.remove(name)
                        break
                    if len(chunk) + downloaded_sizes[name] > file_sizes[name]:
                        chunk = chunk[:(file_sizes[name] - downloaded_sizes[name])]
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
            elif pri == "HIGH":
                i = 5
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        listFile.remove(file)
                        listPri.remove(pri)
                        listFileName.remove(name)
                        break
                    if len(chunk) + downloaded_sizes[name] > file_sizes[name]:
                        chunk = chunk[:(file_sizes[name] - downloaded_sizes[name])]
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
            else :
                i = 2
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[0:16] == b"end_of_this_file":
                        file.close()
                        listFile.remove(file)
                        listPri.remove(pri)
                        listFileName.remove(name)
                        break
                    if len(chunk) + downloaded_sizes[name] > file_sizes[name]:
                        chunk = chunk[:(file_sizes[name] - downloaded_sizes[name])]
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
        #printProgress
        print_progress_all(downloaded_sizes, file_sizes)            
    print("Complete downloading")
    time.sleep(2)

def main():
    host = "10.124.4.121"
    server_address = (host, 23127)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        files_list = client_socket.recv(1024).decode()
        q = queue.Queue()
        readFile = threading.Thread(target=getFile, args=(q,checking))
        readFile.start()
        while True:
            sys.stdout.write("\033c")  # Clear screen
            print("Files available for download:\n" + files_list)
            time.sleep(1)
            
            inFile = q.get()
            requested_files = inFile.split("\n")
            fileName = []
            priority = []
            message = ""
            for file in requested_files:
                name, pri = file.split(" ")
                if os.path.exists(name) == True:
                    continue
                fileName.append(name)
                priority.append(pri)
                message = message + name + " " + pri + "\n"
            if fileName != []:
                downloadFiles(client_socket, fileName, priority, message)
                
        
        
    except KeyboardInterrupt:
        print("\nClient is shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()