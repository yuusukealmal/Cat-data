import os, requests
import re, json, zipfile
import subprocess
from datetime import datetime, timedelta
from git import Repo

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

def version_notify(cc: str, old: str, new: str):
    webhook_url = os.getenv("WEBHOOK")

    names = {"tw": "貓咪大戰爭", "jp": "にゃんこ大戦争", "en": "The Battle Cats", "kr": "냥코 대전쟁"}
    packages = {"tw": "tw", "jp": "", "en": "en", "kr": "kr"}
    
    name = names.get(cc, "The Battle Cats")
    package = packages.get(cc, "")
    image = package if package else "jp"

    data = {
        "embeds": [
            {
                "title": "Battle Cats Update Notifier",
                "description": (
                    f"**{name}** ({cc.upper()})\n\n"
                    f"PackageName: **jp.co.ponos.battlecats{package}**\n\n"
                    f"Version: **{old} → {new}**"
                ),
                "color": 5814783,
                "thumbnail": {
                    "url": f"https://github.com/yuusukealmal/Cat-data/raw/refs/heads/main/assets/{image}.png"
                }
            }
        ]
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        print("Webhook sent successfully!")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def git_push(method: str, msg: str=None):
    t = datetime.utcnow() + timedelta(hours=8)
    t_str = t.strftime("%Y-%m-%d %H:%M:%S")

    try:
        repo = Repo(os.getenv("REPO"))
        origin = repo.remote(name='origin')

        branch = repo.head.ref.name

        if repo.is_dirty(untracked_files=True) or repo.index.diff(None):
            if method == "add":
                repo.git.add(all=True)
                commit = repo.index.commit(msg)
                md5 = commit.hexsha[:7]
                print(f"{t_str} {md5} {msg}")

        if method == "push":
            local = repo.head.commit
            remote = origin.refs[branch].commit

            if local != remote:
                origin.push(refspec=f"{branch}:{branch}")
                print(f"{t_str} Changes were pushed to the {branch} branch.")
            else:
                print(f"{t_str} No new commits to push for the {branch} branch.")
        else:
            print(f"{t_str} No changes to commit or push.")

    except Exception as e:
        print(f"{t_str} Some error occurred while pushing the code:", e)