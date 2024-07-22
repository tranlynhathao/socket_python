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
host = "127.0.0.1"
port = 63353
encoding = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

print("Connected successfully")

def print_progress(current, total, message):
    progress = float(current) / float(total) * 100
    print(f"\rDownloading File{message}.zip... {progress:.2f}%", end='')

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

message = client.recv(1024).decode(encoding)
print(f"{message} \n")

while True:
    message = None
    
    with open("input.txt", "r") as file:
        lines = file.readlines()
        
    for line in lines:
        data = line.strip()
        if not data:
            continue
    
        message = int(data[4])
        if not os.path.exists(f"{output_dir}/File{message}.zip"):
            client.sendall(str(message).encode(encoding))
            
            response = client.recv(1024).decode(encoding)
            print("response {response} \n")
            size = int(response)
            file_name = f"{output_dir}/File{message}.zip"
            
            with open(file_name, "wb") as file:
                current = 0
                while True:
                    chunk = client.recv(1024)
                    if chunk == b"<ENDGAMEEHAHAHA>":
                        break
                    client.sendall(b"ACK")
                    file.write(chunk)
                    current += len(chunk)
                    print_progress(current, size, message)
                print("\n")
    
    print(f"Reached end of input.txt. Please waiting 2 seconds to read it again \n")
    sleep(2)  # Sleep before starting over

    
client.close()
