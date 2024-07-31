import queue
import socket
import threading
import time
import sys
import os
import signal
from tqdm import tqdm

code = "utf-8"

q = queue.Queue()
openedFile = []
file_sizes = {}
fileName = []
filepri = []
output_dir = "output"

def signal_handler(sig, frame):
    print('\nExiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def downloadFiles(client, fileNamee, filepri, message):
    client.sendall(message.encode(code))
    for file in fileNamee:
        openedFile.append(open(f"{output_dir}/{file}", "wb"))
    
    for file in fileNamee:
        data = client.recv(50).decode(code)
        client.sendall(b"ACK")
        file_sizes[file] = int(data)
    
    downloaded_sizes = {file: 0 for file in fileNamee}
    progress_bars = {}

    for file, size in file_sizes.items():
        progress_bars[file] = tqdm(total=size, unit='B', unit_scale=True, desc=file)

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
                            if not os.path.exists(f"{output_dir}/{newName}") and newName not in progress_bars:
                                openedFile.append(open(f"{output_dir}/{newName}", 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(1024)
                                file_sizes[newName] = int(sizeNew.decode(code))
                                progress_bars[newName] = tqdm(total=file_sizes[newName], unit='B', unit_scale=True, desc=newName)
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
                        progress_bars[name].close()
                        del progress_bars[name]
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
                    progress_bars[name].update(len(chunk))
            elif pri == "HIGH":
                i = 5
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[:15] == b"NewFileIsComing":
                        for newName in fileName:
                            if not os.path.exists(f"{output_dir}/{newName}") and newName not in progress_bars:
                                openedFile.append(open(f"{output_dir}/{newName}", 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(1024)
                                file_sizes[newName] = int(sizeNew.decode(code))
                                progress_bars[newName] = tqdm(total=file_sizes[newName], unit='B', unit_scale=True, desc=newName)
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
                        progress_bars[name].close()
                        del progress_bars[name]
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
                    progress_bars[name].update(len(chunk))
            else:
                i = 2
                while i := i - 1:
                    chunk = client.recv(1024)
                    while len(chunk) != 1024:
                        chunkmini = client.recv(1024 - len(chunk))
                        chunk += chunkmini
                    if chunk[:15] == b"NewFileIsComing":
                        for newName in fileName:
                            if not os.path.exists(f"{output_dir}/{newName}") and newName not in progress_bars:
                                openedFile.append(open(f"{output_dir}/{newName}", 'wb'))
                                downloaded_sizes[newName] = 0
                                sizeNew = client.recv(1024)
                                file_sizes[newName] = int(sizeNew.decode(code))
                                progress_bars[newName] = tqdm(total=file_sizes[newName], unit='B', unit_scale=True, desc=newName)
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
                        progress_bars[name].close()
                        del progress_bars[name]
                        break
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
                    progress_bars[name].update(len(chunk))
        
    for bar in progress_bars.values():
        bar.close()
    q.get()
    tqdm.write("Complete downloading")
    client.sendall(b"close__thread")

def main():
    server_address = ('192.168.88.116', 23127)
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
                if os.path.exists(f"{output_dir}/{name}"):
                    continue
                key = 1
                fileName.append(name)
                filepri.append(pri)
                message = message + name + " " + pri + "\n"
                
            if fileName != [] and q.empty() and key == 1:
                key = 0
                q.put(1)    
                downloadThread = threading.Thread(target=downloadFiles, args=(client_socket, fileName, filepri, message))
                downloadThread.start()
            elif fileName != [] and not q.empty() and key == 1:
                key = 0
                client_socket.sendall(b"NewFileDetect")
                client_socket.sendall(message.encode(code))
            time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nClient is shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    main()
