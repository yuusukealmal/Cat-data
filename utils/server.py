import sys, os, zipfile, time
import struct
from .funcs import check
import requests, ua_generator
from .cloudfront import CloudFront

class LIB:
    def __init__(self, lib: bytes, cc: str):
        self.data = lib
        self.cc = cc
        self.start_bytes = self.get_list(cc)
        self.start_address = self.get_start_address()
        self.end_address = self.get_end_memory()
        self.length = (self.end_address - self.start_address) // 4

    def get_list(self, cc: str):
        if cc == "jp":
            start_bytes = [5, 5, 5, 7000000]
        elif cc == "en":
            start_bytes = [3, 2, 2, 6100000]
        elif cc == "kr":
            start_bytes = [3, 2, 1, 6100000]
        elif cc == "tw":
            start_bytes = [2, 3, 1, 6100000]
        return start_bytes
    
    def get_start_address(self):
        start = b"".join(integer.to_bytes(4, "little") for integer in self.start_bytes)
        return self.data.find(start)
    
    def get_end_address1(self):
        return self.data.find(0xFFFFFFFF.to_bytes(4, "little"), self.start_address)
    
    def get_end_address2(self):
        end = b"".join(integer.to_bytes(4, "little") for integer in [0, 0, 0, 0])
        return self.data.find(end, self.start_address)
    
    def get_end_memory(self):
        end1 = self.get_end_address1()
        end2 = self.get_end_address2()
        return min(end1, end2)
    
    def read_bytes(self, length: int):
        result = self.data[self.start_address : self.start_address + length]
        self.start_address += length
        return result
    
    def read_int_list(self):
        result = []
        for _ in range(self.length):
            res = self.read_bytes(4)
            result.append(struct.unpack("<i", res)[0])
        return result
    
    def get_versions(self):
        return self.read_int_list()

class SERVER:
    def __init__(self, file: str, cc: str):
        self.file = file
        self.cc = cc
        self.lib = self.get_lib_file()
        self.versions = LIB(self.lib, self.cc).get_versions()
        self.package = self.get_package_name()
        self.ua  = self.get_ua()
        self.download_link = "https://nyanko-assets.ponosgames.com/iphone/{package}/download/{version}.zip"
    
    def get_lib_file(self):
        _lib = None
        architectures = ["x86", "x86_64", "arm64_v8a", "armeabi_v7a", "armeabi", "mips", "mips64"]
        with zipfile.ZipFile(self.file, "r") as zip:
            for name in zip.namelist():
                if any(arch in name for arch in architectures):
                    _tmp = zip.extract(name)

        with zipfile.ZipFile(_tmp, "r") as zip:
            for name in zip.namelist():
                if "libnative-lib.so" in name :
                    _lib = zip.read(name)
        # os.remove(self.file)
        os.remove(_tmp)
        return _lib
    
    def get_package_name(self):
        cc = "" if self.cc == "jp" else self.cc
        return "battlecats{}".format(cc)
    
    def get_ua(self):
        return str(ua_generator.generate(device="mobile", platform="android"))

    def get_zip_link(self, index: int):
        version = self.versions[index]
        
        if version < 1000000:
            version = "{}_{}_{}".format(self.package, version, index)
        else:
            version = "{}_{:06d}_{:02d}_{:02d}".format(self.package, version // 100, index, version % 100)

        url = self.download_link.format(package = self.package, version = version)
        return url
    
    def download_zip(self, index: int):
        c = CloudFront()
        sign = c.generate_signed_cookie("https://nyanko-assets.ponosgames.com/*")
        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "cookie": sign,
            "range": "bytes=0-",
            "user-agent": self.ua
        }
        url = self.get_zip_link(index)
        r = requests.get(url, headers=headers, stream=True)
        while len(r.content) == 243:
            print("retry {}".format(index))
            r = requests.get(url, headers=headers, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                with open(f"./assets{index}.zip", "ab") as f:
                    f.write(chunk)
        self.PACK = env.PACK.value
        self.zip = zip
        self.cc = cc

def server(apk: str=None, xapk: str=None):
    if not (apk or xapk):
        print("Please select a file")
        sys.exit(1)

    _is_valid = check(apk, xapk)
    if not _is_valid:
        print(f"Invalid file: {apk or xapk}. Please select a valid game file.")
        sys.exit(1)
        
    cc = "jp" if _is_valid.endswith("battlecats") else _is_valid[-2:]
    process(SERVER((apk or xapk), cc))

def process(pkg: SERVER):
    for i in range(len(pkg.versions)):
        pkg.download_zip(i)
        time.sleep(5)