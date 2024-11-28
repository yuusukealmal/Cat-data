import argparse
from utils.bcuzip import bcuzip
from utils.event import event

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_bcuzip = subparsers.add_parser("bcuzip", help="Process a file or folder of certain game emulator files")
    parser_bcuzip.add_argument("--file", help="Path to a certain game emulator file")
    parser_bcuzip.add_argument("--folder", help="Path to a certain game emulator folder")
    
    parser_event = subparsers.add_parser("event", help="Get events of .tsv files of a certain game")
    parser_event.add_argument("--old", action="store_true", help="Get files from the old way")
    parser_event.add_argument("--new", action="store_true", help="Get files from the new way")

    args = parser.parse_args()

    if args.command == "bcuzip":
        bcuzip(file=args.file, folder=args.folder)
    elif args.command == "event":
        event(old=args.old, new=args.new)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()