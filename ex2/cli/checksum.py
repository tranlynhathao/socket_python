import hashlib

def calculate_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

original_md5 = calculate_md5("original_file.zip")
downloaded_md5 = calculate_md5("downloaded_file.zip")

if original_md5 == downloaded_md5:
    print("File downloaded successfully and is identical to the original.")
else:
    print("File downloaded but is different from the original.")
