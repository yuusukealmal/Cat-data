import argparse
from utils.bcuzip import bcuzip


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")


    args = parser.parse_args()

    if args.command == "bcuzip":
        bcuzip(file=args.file, folder=args.folder)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()