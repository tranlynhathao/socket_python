import socket
import signal
import sys
import os
from time import sleep

# Signal handler to exit program
def signal_handler(sig, frame):
    print('\nExiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Client configuration
host = "192.168.0.101"
port = 23127
encoding = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

print("Connected successfully")

def print_progress(current, total, message):
    progress = float(current) / float(total) * 100
    print(f"\rDownloading File {message}... {progress:.2f}%", end='')

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

message = client.recv(1024).decode(encoding)
print(f"{message} \n")

while True:
    with open("input.txt", "r") as file:
        lines = file.readlines()
        
    for line in lines:
        data = line.strip()
        if not data:
            continue
    
        message = data      
        if not os.path.exists(f"{output_dir}/{message}"):
            client.sendall(str(message).encode(encoding))
            
            response = client.recv(1024).decode(encoding)
            size = int(response)    
            file_name = f"{output_dir}/{message}"
            
            with open(file_name, "wb") as file:
                current = 0
                while True:
                    chunk = client.recv(1024)
                    if chunk == b"<EndOfFile>":
                        break
                    while len(chunk) != 1024:
                        data = client.recv(1024 - len(chunk))
                        chunk = chunk + data
                    file.write(chunk)
                    current += len(chunk)
                    print_progress(current, size, message)
                print("\n")
    print("Reached end of input.txt. Please wait 2 seconds to read it again\n")
    sleep(2)  # Sleep before starting over

# client.close()
