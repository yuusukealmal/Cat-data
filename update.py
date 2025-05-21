from util.placement import placement
from util.event import event
from util.local import local

from dotenv import load_dotenv
from util.funcs import git_push


if __name__ == "__main__":
    load_dotenv()
    placement(notify=True)
    git_push("push")
    event(new=True)
    git_push("push")
    # local(way="latest", remote=True)
    # git_push("push")