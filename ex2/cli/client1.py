# import socket
# import signal
# import sys
# import os
# from time import sleep

# # Signal handler to exit program
# def signal_handler(sig, frame):
#     print('\nExiting program...')
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)

# # Client configuration
# host = "192.168.0.101"
# port = 23127
# encoding = "utf-8"

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect((host, port))

# print("Connected successfully")

# def print_progress(current, total, message):
#     progress = float(current) / float(total) * 100
#     print(f"\rDownloading File {message}... {progress:.2f}%", end='')

# output_dir = "output"
# os.makedirs(output_dir, exist_ok=True)

# message = client.recv(1024).decode(encoding)
# print(f"{message} \n")

# while True:
#     with open("input.txt", "r") as file:
#         lines = file.readlines()
        
#     for line in lines:
#         data = line.strip()
#         if not data:
#             continue
    
#         message = data      
#         if not os.path.exists(f"{output_dir}/{message}"):
#             client.sendall(str(message).encode(encoding))
            
#             response = client.recv(1024).decode(encoding)
#             size = int(response)    
#             file_name = f"{output_dir}/{message}"
            
#             with open(file_name, "wb") as file:
#                 current = 0
#                 while True:
#                     chunk = client.recv(1024)
#                     if chunk == b"<EndOfFile>":
#                         break
#                     while len(chunk) != 1024:
#                         data = client.recv(1024 - len(chunk))
#                         chunk = chunk + data
#                     file.write(chunk)
#                     current += len(chunk)
#                     print_progress(current, size, message)
#                 print("\n")
#     print("Reached end of input.txt. Please wait 2 seconds to read it again\n")
#     sleep(2)  # Sleep before starting over

# # client.close()






import socket
import threading
import time
import sys
import os

def download_file(client_socket, filename, priority, progress, total_size):
    chunk_size = 2048 if priority == "CRITICAL" else 1024 if priority == "HIGH" else 256
    try:
        with open(filename, "wb") as f:
            while progress[filename] < total_size[filename]:
                chunk = client_socket.recv(chunk_size)
                if not chunk:
                    break
                while len(chunk) != chunk_size:
                    chunkmini = client_socket.recv(chunk_size - len(chunk))
                    chunk = chunk + chunkmini
                f.write(chunk)
                progress[filename] += len(chunk)
        print(f"Download successfully: {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def print_progress(progress, total_size):
    while any(size < total_size[filename] for filename, size in progress.items()):
        sys.stdout.write("\033c")  # Clear screen
        for filename, size in progress.items():
            if size < total_size[filename]:
                percentage = (size / total_size[filename]) * 100
                bar_length = 50
                filled_length = int(bar_length * percentage // 100)
                bar = '#' * filled_length + '-' * (bar_length - filled_length)
                print(f"{filename} |{bar}| {percentage:.2f}%")
            else:
                print(f"{filename} | Download successfully")
        sys.stdout.flush()
        time.sleep(1)
    print("Download complete")

def request_files(client_socket, files_list, last_requested_files):
    try:
        with open("input.txt", "r") as f:
            requested_files = f.read().strip()

        if requested_files != last_requested_files:
            client_socket.sendall(requested_files.encode())
            threads = []
            progress = {}
            total_size = {}

            for requested_file in requested_files.split("\n"):
                if requested_file.strip():
                    filename, priority = requested_file.split()
                    total_size[filename] = int([file for file in files_list.split("\n") if file.startswith(filename)][0].split()[1][:-2]) * 1024 * 1024
                    progress[filename] = 0
                    t = threading.Thread(target=download_file, args=(client_socket, filename, priority, progress, total_size))
                    threads.append(t)
                    t.start()

            progress_thread = threading.Thread(target=print_progress, args=(progress, total_size))
            progress_thread.start()

            for t in threads:
                t.join()

            progress_thread.join()

        return requested_files
    except Exception as e:
        print(f"Error requesting files: {e}")
        return last_requested_files

def main():
    server_address = ('localhost', 23127)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        files_list = client_socket.recv(1024).decode()
        print("Files available for download:\n", files_list)

        last_requested_files = ""
        while True:
            last_requested_files = request_files(client_socket, files_list, last_requested_files)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nClient is shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()