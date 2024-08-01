import queue
import socket
import threading
import time
import sys
import os
import signal
import argparse
import colorama

code = "utf-8"

# Argument parser configuration
parser = argparse.ArgumentParser(description="Client to download files from server")
parser.add_argument('--host', type=str, required=True, help='Server host')
parser.add_argument('--port', type=int, required=True, help='Server port')
args = parser.parse_args()

host = args.host
port = args.port

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

def print_progress_all(downloaded_sizes, file_sizes):
    sys.stdout.write("\033c")  # Clear screen
    for file_name in downloaded_sizes:
        progress_percentage = (float(downloaded_sizes[file_name]) / file_sizes[file_name]) * 100
        bar_length = 50  # Length of the progress bar
        filled_length = int(bar_length * progress_percentage // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        color = colorama.Fore.LIGHTYELLOW_EX
        if filled_length == 50:
            color = colorama.Fore.LIGHTGREEN_EX
        print(color + f"Downloading {file_name} |{bar}| {progress_percentage:.2f}%\n")
    #time.sleep(0.0001)

def downloadFiles(client, fileNamee, filepri, message):
    client.sendall(message.encode(code))
    for file in fileNamee:
        openedFile.append(open(f"{output_dir}/{file}", "wb"))
    
    for file in fileNamee:
        data = client.recv(16).decode(code)
        client.sendall(b"ACK")
        file_sizes[file] = int(data)
    
    downloaded_sizes = {file: 0 for file in fileNamee}

    while fileNamee != []:
        for file, pri, name in zip(openedFile, filepri, fileNamee):
            if pri == "CRITICAL":
                i = 11
            elif pri == "HIGH":
                i = 5
            else :
                i = 2
            while i := i - 1:
                chunk = client.recv(1024)
                while len(chunk) != 1024:
                    chunkmini = client.recv(1024 - len(chunk))
                    chunk += chunkmini
                if chunk[:15] == b"NewFileIsComing":
                    for newName in fileName:
                        if not os.path.exists(f"{output_dir}/{newName}"):
                            openedFile.append(open(f"{output_dir}/{newName}", 'wb'))
                            downloaded_sizes[newName] = 0
                            sizeNew = client.recv(16)
                            file_sizes[newName] = int(sizeNew.decode(code))
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
                if downloaded_sizes[name] + 1024 > file_sizes[name]:
                    file.write(chunk[:(file_sizes[name] - downloaded_sizes[name])])
                    downloaded_sizes[name] = downloaded_sizes[name] + file_sizes[name] - downloaded_sizes[name]
                else:
                    file.write(chunk)
                    downloaded_sizes[name] += len(chunk)
        
            print_progress_all(downloaded_sizes, file_sizes)
    q.get()
    print(colorama.Fore.RESET)
    print("Complete downloading")
    client.sendall(b"close__thread")

def main():
    server_address = (host, port)
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
                if file == "":
                    break
                name, pri = file.split(" ")
                if os.path.exists(f"{output_dir}/{name}") or name in fileName:
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
