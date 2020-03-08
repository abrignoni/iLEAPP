import argparse
from time import process_time

from extraction import *


parser = argparse.ArgumentParser(
    description="iLEAPP: iOS Logs, Events, and Preferences Parser."
)
parser.add_argument(
    "-o",
    choices=["fs", "tar", "zip"],
    required=True,
    action="store",
    help="Directory path, TAR, or ZIP filename and path(required).",
)
parser.add_argument("pathtodir", help="Path to directory")

args = parser.parse_args()
pathto = args.pathtodir
extracttype = args.o

start = process_time()
log = pre_extraction(pathto)
extract_and_process(pathto, extracttype, tosearch, log)
running_time = post_extraction(start, extracttype, pathto)
