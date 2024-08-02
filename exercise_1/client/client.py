import socket
import signal
import sys
import os
from time import sleep
import colorama
import argparse

# Signal handler to exit program
def signal_handler(sig, frame):
    print('\nExiting program...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Argument parser configuration
parser = argparse.ArgumentParser(description="Client to download files from server")
parser.add_argument('--host', type=str, required=True, help='Server host')
parser.add_argument('--port', type=int, required=True, help='Server port')
args = parser.parse_args()

host = args.host
port = args.port
encoding = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

print("Connected successfully")

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

message = client.recv(1024).decode(encoding)
print(f"{message} \n")

def print_process(current, total, fileName):
    percent = float(current) / total * 100
    bar_length = 50  # Length of the progress bar
    filled_length = int(bar_length * percent // 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    color = colorama.Fore.LIGHTYELLOW_EX
    print(color + f"\rDownloading {fileName} |{bar}| {percent:.2f}%", end='', flush=True)
    if filled_length == 50:
        color = colorama.Fore.LIGHTGREEN_EX
        print(color + f"\rDownloading {fileName} |{bar}| {percent:.2f}%", end='\r', flush=True)
    #print(colorama.Fore.RESET)

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
                    while len(chunk) != 1024:
                        data = client.recv(1024 - len(chunk))
                        chunk = chunk + data
                    if chunk[:11] == b"<EndOfFile>":
                        break
                    if current + 1024 > size:
                        file.write(chunk[0:(size - current)])
                        current = current + (size - current)
                    else:    
                        file.write(chunk)
                        current += len(chunk)
                    print_process(current, size, message)
            print("\n")
            print(colorama.Fore.RESET)

# client.close()
