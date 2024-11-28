import argparse
from utils.bcuzip import bcuzip


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_bcuzip = subparsers.add_parser("bcuzip", help="Process a file or folder of certain game emulator files")
    parser_bcuzip.add_argument("--file", help="Path to a certain game emulator file")
    parser_bcuzip.add_argument("--folder", help="Path to a certain game emulator folder")

    args = parser.parse_args()

    if args.command == "bcuzip":
        bcuzip(file=args.file, folder=args.folder)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()