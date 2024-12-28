from utils.event import event
from utils.local import local

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from git import Repo

def git_push(msg: str):
    t = datetime.utcnow() + timedelta(hours=8)
    t_str = t.strftime("%Y-%m-%d %H:%M:%S")

    try:
        repo = Repo(os.getenv("REPO"))

        if repo.is_dirty(untracked_files=True) or repo.index.diff(None):
            repo.git.add(update=True)
            commit = repo.index.commit(msg)
            md5 = commit.hexsha[:7]
            origin = repo.remote(name='origin')
            origin.push()
            print(f"{t_str} {md5} Changes were pushed to the repository.")
        else:
            print(f"{t_str} No changes to commit or push.")

    except Exception as e:
        print(f"{t_str} Some error occurred while pushing the code:", e) 

if __name__ == "__main__":
    load_dotenv()
    event(new=True)
    git_push("Update Certain Game Event Data")
    local(way="latest", remote=True)
    git_push("Update Certain Game Data")