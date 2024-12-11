from utils.event import event
from utils.local import local

import os
from dotenv import load_dotenv
from git import Repo

def git_push():
    load_dotenv()
    try:
        repo = Repo(os.getenv("REPO"))

        if repo.is_dirty(untracked_files=True) or repo.index.diff(None):
            repo.git.add(update=True)
            repo.index.commit("Update Certain Game Data")
            origin = repo.remote(name='origin')
            origin.push()
            print("Changes were pushed to the repository.")
        else:
            print("No changes to commit or push.")

    except Exception as e:
        print('Some error occurred while pushing the code:', e) 

if __name__ == "__main__":
    event(new=True)
    local(way="latest", remote=True)
    git_push()