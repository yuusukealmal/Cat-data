from util.event import event
from util.local import local

from dotenv import load_dotenv
from util.funcs import git_push


if __name__ == "__main__":
    load_dotenv()
    event(new=True)
    git_push("push")
    local(way="latest", remote=True)
    git_push("push")