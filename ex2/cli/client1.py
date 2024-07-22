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
                f.write(chunk)
                progress[filename] += len(chunk)
                client_socket.sendall(b'ack')
                time.sleep(0.00001)
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
    server_address = ('localhost', 3001)
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
