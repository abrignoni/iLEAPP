import argparse
import sys
from time import process_time

from extraction import *


parser = argparse.ArgumentParser(
    description="iLEAPP: iOS Logs, Events, and Preferences Parser."
)
parser.add_argument("pathtodir", nargs='?', help="Path to directory")
parser.add_argument("--gui", action="store_true", help="To run program with the GUI client")

args = parser.parse_args()
image_fpath = args.pathtodir
gui = args.gui

if sum([gui, bool(image_fpath)]) < 1:
    print("[ERROR] Please provide at least one argument. Run `$ python ileapp.py -h` for help")
    sys.exit(1)

if gui:
    import PySimpleGUI as sg
    from ileappGUI import layout, gui_event_loop
    window = sg.Window("iLEAPP", layout)
    gui_event_loop(window)


start = process_time()
log = pre_extraction(image_fpath)
extracttype = get_filetype(image_fpath)
extract_and_process(image_fpath, extracttype, tosearch, log)
running_time = post_extraction(start, extracttype, image_fpath)
