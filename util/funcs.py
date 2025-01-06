import os
import re, json, zipfile
import subprocess

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