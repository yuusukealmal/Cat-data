import sys, re, os, zipfile, json
from enum import Enum
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
import hashlib
import requests
from bs4 import BeautifulSoup as bs4
import ua_generator
from .funcs import check, version_notify
from .server import server
from .funcs import git_push

class env(Enum):
    LIST = 'b484857901742afc'
    PACK = '89a0f99078419c28'
    JP_PACK = 'd754868de89d717fa9e7b06da45ae9e3'
    JP_IV = '40b2131a9f388ad4e5002a98118f6128'
    EN_PACK = '0ad39e4aeaf55aa717feb1825edef521'
    EN_IV = 'd1d7e708091941d90cdf8aa5f30bb0c2'
    TW_PACK = '313d9858a7fb939def1d7d859629087d'
    TW_IV = '0e3743eb53bf5944d1ae7e10c2e54bdf'
    KR_PACK = 'bea585eb993216ef4dcb88b625c3df98'
    KR_IV = '9b13c2121d39f1353a125fed98696649'

class APK:
    def __init__(self, way: str, path: str, cc: str):
        self.path = path
        self.cc = cc
        self.way = way
        self.package = self.get_package()
        self.LIST_KEY = env.LIST.value
        if way=="new":
            self.PACK_KEY, self.IV_KEY = self.get_pack_iv()
        else:
            self.PACK_KEY = self.get_pack()
        self.itmes = self.get_items()
        self.bcu = []

    def get_package(self):
        return "jp.co.ponos.battlecats" + self.cc
    
    def get_pack_iv(self):
        mapping = {
            'jp': (env.JP_PACK.value, env.JP_IV.value),
            'en': (env.EN_PACK.value, env.EN_IV.value),
            'tw': (env.TW_PACK.value, env.TW_IV.value),
            'kr': (env.KR_PACK.value, env.KR_IV.value),
        }
        return mapping.get(self.cc, (None, None)) 
    
    def get_pack(self):
        return env.PACK.value
    
    def get_items(self):
        with zipfile.ZipFile(self.path, "r") as zip:
            return [i.split(".")[:-1][0] for i in zip.namelist() if i.endswith(".pack")]
        
    def parse(self):
        for _ in self.itmes:
            _item = ITEM(self.way, self.path, self.cc, _)
            _item.parse()
            del _item

class ITEM(APK):
    def __init__(self, way: str, path: str, cc: str, item: str):
        super().__init__(way, path, cc)
        self.item = item
        self.PACK = self.get_PACK()
        self.LIST_AES = self.get_key_aes()
        self.list = self.get_LIST()
        self.folder = self.get_folder()
    
    def get_PACK(self):
        with zipfile.ZipFile(self.path, "r") as zip:
            _pack = zip.read(f"{self.item}.pack")
        return _pack
    
    def get_key_aes(self):
        _aes = AES.new(self.LIST_KEY.encode("utf-8"), AES.MODE_ECB)
        return _aes

    def get_aes(self):
        if self.way == "new":
            _aes = AES.new(bytes.fromhex(self.PACK_KEY), AES.MODE_CBC, bytes.fromhex(self.IV_KEY))
        else:
            _aes = AES.new(bytes(self.PACK_KEY, "utf-8"), AES.MODE_ECB)
        return _aes

    def get_LIST(self):
        with zipfile.ZipFile(self.path, "r") as zip:
            data = zip.read(f"{self.item}.list")
            _list = self.LIST_AES.decrypt(data)
        list = unpad(_list, AES.block_size).decode("utf-8")
        return list
    
    def get_folder(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_dir = os.path.join(base_dir, "Data", "local", self.package, self.item.split("/")[-1])
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def get_DATA(self, start: int, arrange: int):
        return self.PACK[start:start + arrange]
    
    def delete_padding(self, pack_res: bytes):
        padding_map = {
            b'\x00': 1, b'\x01': 1, b'\x02': 2, b'\x03': 3, b'\x04': 4, b'\x05': 5,
            b'\x06': 6, b'\x07': 7, b'\x08': 8, b'\t': 9, b'\n': 10, b'\x0b': 11, 
            b'\x0c': 12, b'\r': 13, b'\x0e': 14, b'\x0f': 15, b'\x10': 16
        }
        last = pack_res[-1:]
        padding_count = padding_map.get(last, 0)
        return pack_res[:-padding_count] if padding_count > 0 else pack_res

    def to_file(self, name: str, data: bytes):
        with open(os.path.join(self.folder, name), "wb") as f:
            f.write(data)

    def get_hash(self, data: str|bytes):
        if isinstance(data, str):
            return hashlib.md5(open(data, 'rb').read()).hexdigest()
        if isinstance(data, bytes):
            return hashlib.md5(data).hexdigest()

    def parse(self):
        for _line in self.list.splitlines()[1:]:
            name, start, arrange = _line.split(",")
            _data = self.get_DATA(int(start), int(arrange))
            _path = os.path.join(self.folder, name)

            if "ImageDataLocal" not in self.item:
                _data = self.delete_padding(self.get_aes().decrypt(_data))

            if (not os.path.exists(_path)) or (self.get_hash(_path) != self.get_hash(_data)):
                if self.cc == "jp" and any([i in name for i in ["imgcut", "mamodel", "maanim"]]) and self.item == "NumberLocal":
                    self.bcu.append(name.split(".")[0])
                self.to_file(name, _data)
        self.delete()
                
    def delete(self):
        files = [i.split(",")[0] for i in self.list.splitlines()[1:]]
        for f in os.listdir(self.folder):
            if f not in files:
                os.remove(os.path.join(self.folder, f))

def get_latest_version(cc: str):
    ua = str(ua_generator.generate())
    with open(os.path.join(os.getcwd(), "version.json"), "r") as f:
        j = json.load(f)
    r = requests.get(j[cc]["version_url"], headers={"User-Agent": str(ua)})
    soup = bs4(r.content, "lxml")
    meta = soup.find('meta', attrs={'name': 'description'})
    content = meta.get('content')
    version = re.search(r'\b\d+\.\d+\.\d+\b', content).group()
    return version

def parse_version_int(version: str):
    return int("".join([_.zfill(2) for _ in version.split(".")]))

def parse_version_str(version: int):
    version_str = str(version)
    return ".".join(version_str[i:i+2].lstrip("0") or "0" for i in range(0, len(version_str), 2))

def check_version():
    ls = []
    with open(os.path.join(os.getcwd(), "version.json"), "r") as f:
        j = json.load(f)
    for i in ["JP", "TW", "EN", "KR"]:
        _version = j[i]["version"]
        version = get_latest_version(i)
        if _version < parse_version_int(version):
            ls.append(i)
            j[i]["version"] = parse_version_int(version)
            version_notify(i.lower(), parse_version_str(_version), version)
    with open(os.path.join(os.getcwd(), "version.json"), "w") as f:
        json.dump(j, f, indent=4) 
    return ls

def download_apk(version: str):
    ua = str(ua_generator.generate())
    with open(os.path.join(os.getcwd(), "version.json"), "r") as f:
        j = json.load(f)
    r = requests.get(
        url = j[version]["download_url"],
        headers={"User-Agent": str(ua)},
        stream=True,
        timeout=10,
    )
    with open(f"{version}.xapk", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return os.path.abspath(f"{version}.xapk")

def local(way: str, apk=None, xapk=None, remote=False):
    if way != "latest":
        if not (apk or xapk):
            print("Please select a file")
            sys.exit(1)
        
        _is_valid = check(apk, xapk)
        if not _is_valid:
            print(f"Invalid file: {apk or xapk}. Please select a valid game file.")
            sys.exit(1)
        
        cc = "jp" if _is_valid.endswith("battlecats") else _is_valid[-2:]
        
        if xapk:
            with zipfile.ZipFile(xapk, "r") as zip:
                zip.extract("InstallPack.apk")
            xapk = os.path.join(os.getcwd(), "InstallPack.apk")

        process(APK(way, apk or xapk, cc))
        os.remove(apk or xapk)
        
    else:
        _process = check_version()
        for i in _process:
            _path = download_apk(i)
            with zipfile.ZipFile(_path, "r") as zip:
                zip.extract("InstallPack.apk")
            xapk = os.path.join(os.getcwd(), "InstallPack.apk")
            process(APK("new", xapk, i.lower()))
            git_push("add", f"Update Certain Game {i.upper()} Local Files")
            os.remove(xapk)
            if remote:
                server(xapk=_path)
                git_push("add", f"Update Certain Game {i.upper()} Server Files")
            try:
                os.remove(_path)
            except:
                pass
        
def process(pkg: APK):
    pkg.parse()
    print(pkg.bcu)
    # parse(set(pkg.bcu))