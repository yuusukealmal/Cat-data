import sys, os, hashlib, json
from Crypto.Cipher import AES

class Bcuzip:
    def __init__(self, file: str):
        self.title = None
        self.bytes = open(file, "rb").read()
        self.length = int.from_bytes(self.bytes[0x20:0x24], "little")
        self.pad = 16 * (self.length // 16 + 1)
        self.data = self.bytes[0x24 + self.pad:]
        self.key = self.bytes[0x10:0x20]
        self.iv = hashlib.md5("battlecatsultimate".encode("utf-8")).digest()[0:16]
        self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.info = self.get_info()

    def get_info(self):
        _info = self.aes.decrypt(self.bytes[0x24 : 0x24 + self.pad])[0:self.length]
        info = json.loads(_info)
        self.title = info["desc"]["id"] or info["desc"]["names"]["dat"][0]["val"]
        return info

    def write_files(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_dir = os.path.join(base_dir, "Data", "bcuzip", self.title)
        os.makedirs(target_dir, exist_ok=True)
        
        with open(os.path.join(target_dir, "info.json"), "w") as f:
            json.dump(self.info, f, indent=4)
        for _ in self.info["files"]:
            file = os.path.join(target_dir, *_['path'].split('/')[1:])
            os.makedirs(os.path.dirname(file), exist_ok=True)

            size, offset = _["size"], _["offset"]
            data = AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(self.data[offset:offset + (size + (16 - size % 16))])[:size]

            if "pack.json" in file:
                with open(file, "w") as f:json.dump(json.loads(data), f, indent=4)
            else:
                with open(file, "wb") as f:f.write(data)

def bcuzip(file: str=None, folder: str=None):
    if file is None and folder is None:
        print("Please select a file or folder")
        sys.exit(1)

    if file:
        process(file)

    if folder:
        if not os.path.isdir(folder):
            print("Please select a folder")
            sys.exit(1)
        for file in os.listdir(folder):
            if file.endswith(".bcuzip"):
                if file.endswith(".bcuzip"):
                    process(os.path.join(folder, file))

def process(file: str):
    if not file.endswith(".bcuzip"):
        print(f"Invalid file: {file}. Please select a .bcuzip file.")
        return
    try:
        bcuzip = Bcuzip(file)
        bcuzip.write_files()
        del bcuzip
    except Exception as e:
        print(f"Error processing {file}: {e}")
        sys.exit(1)
