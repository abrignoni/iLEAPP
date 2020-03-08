import argparse
import glob
import os
import re
import shutil
import sys
import tarfile
from argparse import RawTextHelpFormatter
from tarfile import TarFile
from time import process_time
from zipfile import ZipFile

from six.moves.configparser import RawConfigParser

from ilapfuncs import *
from report import *
from search_files import *
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

start = process_time()

args = parser.parse_args()

pathto = args.pathtodir
extracttype = args.o
start = process_time()

os.makedirs(reportfolderbase)
os.makedirs(reportfolderbase + "Script Logs")

log = pre_extraction()

if extracttype == "fs":
    for key, val in tosearch.items():
        filefound = search(pathto, val)
        process_file_found(filefound, key, val)
    log.close()


elif extracttype == "tar":
    t = TarFile(pathto)
    for key, val in tosearch.items():
        filefound = search_archive(t, val)
        process_file_found(filefound, key, val)
    log.close()


elif extracttype == "zip":
    z = ZipFile(pathto)

    for key, val in tosearch.items():
        filefound = search_archive(t, val)
        process_file_found(filefound, key, val)

    log.close()
    z.close()

else:
    logfunc("Error on argument -o")

post_extraction(start)
