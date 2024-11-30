import sys, re, os, subprocess, zipfile, json
from enum import Enum
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES

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
    def __init__(self, path: str, cc: str):
        self.path = path
        self.cc = cc
        self.package = self.get_package()
        self.LIST_KEY = env.LIST.value
        self.PACK_KEY, self.IV_KEY = self.get_pack_iv()
        self.itmes = self.get_items()

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
    
    def get_items(self):
        with zipfile.ZipFile(self.path, "r") as zip:
            return [i.split(".")[:-1][0] for i in zip.namelist() if i.endswith(".pack")]
        
    def parse(self):
        for _ in self.itmes:
            _item = ITEM(self.path, self.cc, _)
            _item.parse()
            del _item

class ITEM(APK):
    def __init__(self, path: str, cc: str, item: str):
        super().__init__(path, cc)
        self.item = item
        self.PACK = self.get_PACK()
        self.LIST_AES = self.get_key_aes()
        self.list = self.get_LIST()
        self.folder = self.get_folder()
        self.count = 0
    
    def get_PACK(self):
        with zipfile.ZipFile(self.path, "r") as zip:
            _pack = zip.read(f"{self.item}.pack")
        return _pack
    
    def get_key_aes(self):
        _aes = AES.new(self.LIST_KEY.encode("utf-8"), AES.MODE_ECB)
        return _aes

    def get_aes(self):
        _aes = AES.new(bytes.fromhex(self.PACK_KEY), AES.MODE_CBC, bytes.fromhex(self.IV_KEY))
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
    
    def parse(self):
        for _line in self.list.splitlines()[1:]:
            name, start, arrange = _line.split(",")
            _data = self.get_DATA(int(start), int(arrange))
            if "ImageDataLocal" in self.item:
                data = _data
            else:
                data = self.delete_padding(self.get_aes().decrypt(_data))
            self.to_file(name, data)

def check(apk=None, xapk=None):
    if apk:
        output = subprocess.check_output([os.path.abspath("./utils/aapt2.exe"), "dump", "badging", apk], universal_newlines=True, encoding="utf-8")
        package = re.search(r"name='([^']+)'", output).group(1)
        return package if "jp.co.ponos.battlecats" in package else False

    if xapk:
        with zipfile.ZipFile(xapk, "r") as zip_file:
            manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))
            package = manifest["package_name"]
            return package if "jp.co.ponos.battlecats" in package else False

def local(apk=None, xapk=None):
    if not apk and not xapk:
        print("Please select a file or folder")
        sys.exit(1)
    
    _is_valid = check(apk, xapk)
    if not _is_valid:
        target = apk or xapk
        print(f"Invalid file: {target}. Please select a valid certain game file.")
        sys.exit(1)

    cc = "jp" if _is_valid.endswith("battlecats") else _is_valid[-2:]
    
    if xapk:
        with zipfile.ZipFile(xapk, "r") as zip:
            zip.extract("InstallPack.apk")
            xapk = os.getcwd() + "/InstallPack.apk"
    process(APK(apk, cc) if apk else APK(xapk, cc))
    
def process(pkg: APK):
    pkg.parse()