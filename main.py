import argparse
from utils.bcuzip import bcuzip
from utils.event import event
from utils.local import local

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_bcuzip = subparsers.add_parser("bcuzip", help="Process a file or folder of certain game emulator files")
    parser_bcuzip.add_argument("--file", help="Path to a certain game emulator file")
    parser_bcuzip.add_argument("--folder", help="Path to a certain game emulator folder")
    
    parser_event = subparsers.add_parser("event", help="Get events of .tsv files of a certain game")
    parser_event.add_argument("--old", action="store_true", help="Get files from the old way")
    parser_event.add_argument("--new", action="store_true", help="Get files from the new way")
    
    parser_local = subparsers.add_parser("local", help="Get local files from certain game")

    parser_local_ways = parser_local.add_mutually_exclusive_group(required=True)
    parser_local_ways.add_argument("--old", action="store_true", help="Use the old way")
    parser_local_ways.add_argument("--new", action="store_true", help="Use the new way")
    parser_local_ways.add_argument("--latest", action="store_true", help="Use the latest way")

    parser_local.add_argument("--apk", help="Path to a certain game file (.apk)")
    parser_local.add_argument("--xapk", help="Path to a certain file (.xapk)")

    args = parser.parse_args()

    if args.command == "bcuzip":
        bcuzip(file=args.file, folder=args.folder)
    elif args.command == "event":
        event(old=args.old, new=args.new)
    elif args.command == "local":
        way = "latest" if args.latest else ("new" if args.new else "old")
        local(way=way, apk=args.apk, xapk=args.xapk)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()