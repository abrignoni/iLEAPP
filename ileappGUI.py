import argparse
import glob
import os
import re
import shutil
import sys
import tarfile
import webbrowser
from argparse import RawTextHelpFormatter
from tarfile import TarFile
from time import process_time
from zipfile import ZipFile

import PySimpleGUI as sg
from six.moves.configparser import RawConfigParser

from extraction import *
from ilapfuncs import *
from report import *
from search_files import *
from settings import report_folder_base


# All the stuff inside your window.

sg.theme("DarkAmber")  # Add a touch of color
layout = [
    [
        sg.Text("iOS Logs, Events, And Properties Parser.", font=("Helvetica", 25))
    ],  # added font type and font size
    [
        sg.Text("https://github.com/abrignoni/iLEAPP", font=("Helvetica", 18))
    ],  # added font type and font size
    [
        sg.Text(
            "Select the file type or directory of the target iOS full file system extraction for parsing.",
            font=("Helvetica", 16),
        )
    ],  # added font type and font size
    [
        sg.Text("File:", size=(8, 1), font=("Helvetica", 14)),
        sg.Input(),
        sg.FileBrowse(font=("Helvetica", 12)),
    ],  # added font type and font size
    [
        sg.Text("Directory:", size=(8, 1), font=("Helvetica", 14)),
        sg.Input(),
        sg.FolderBrowse(font=("Helvetica", 12)),
    ],  # added font type and font size
    [
        sg.Checkbox(
            "Generate CSV output (Additional processing time)",
            size=(50, 1),
            default=False,
            font=("Helvetica", 14),
        )
    ],
    [sg.Output(size=(100, 40))],  # changed size from (88,20)
    [
        sg.Submit("Process", font=("Helvetica", 14)),
        sg.Button("Close", font=("Helvetica", 14)),
    ],
]  # added font type and font size


# Create the Window

# Event Loop to process "events" and get the "values" of the inputs
def gui_event_loop(window):
    while True:
        event, values = window.read()
        if event in (None, "Close"):  # if user closes window or clicks cancel
            break

        pathto = values["Browse"] or values["Browse0"]

        extracttype = get_filetype(pathto)
        start = process_time()
        log = pre_extraction(pathto, gui_window=window)
        extract_and_process(pathto, extracttype, tosearch, log, gui_window=window)
        running_time = post_extraction(start, extracttype, pathto)

        if values[2] == True:
            start = process_time()
            window.refresh()
            logfunc("")
            logfunc(f"CSV export starting. This might take a while...")
            window.refresh()
            html2csv(report_folder_base)

        if values[2] == True:
            end = process_time()
            time = start - end
            logfunc("CSV processing time in secs: " + str(abs(time)))

        locationmessage = "Report name: " + report_folder_base + "index.html"
        sg.Popup("Processing completed", locationmessage)

        basep = os.getcwd()
        webbrowser.open_new_tab("file://" + basep + base + "index.html")
        sys.exit()
