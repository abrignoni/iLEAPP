__artifacts_v2__ = {
    "get_walStrings": {
        "name": "Database Journal Strings",
        "description": "Extracts ASCII strings from SQLite Write-Ahead Logs (WAL) and Journals.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-04-30",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Database Metadata",
        "notes": "Generates text files with strings found in WAL/Journal files",
        "paths": ('*/*-wal', '*/*-journal'),
        "output_types": "standard",
        "artifact_icon": "database",
        "html_columns": ['Report']
    }   
}

import os
import re
import string
from pathlib import Path
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc
    )

control_chars = ''.join(map(chr, range(0, 32))) + ''.join(map(chr, range(127, 160)))
not_control_char_re = re.compile(f'[^{control_chars}]' + '{4,}')
printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')


@artifact_processor
def get_walStrings(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()

    x = 1
    data_list = []
    source_path_ref = ''

    for file_found in files_found:
        file_found = str(file_found)

        if not source_path_ref:
            source_path_ref = file_found

        try:
            filesize = Path(file_found).stat().st_size
        except OSError:
            continue

        if filesize == 0:
            continue

        journalName = os.path.basename(file_found)
        output_filename = f"{x}_{journalName}.txt"
        outputpath = os.path.join(report_folder, output_filename)

        unique_items = set()
        out_lines = []

        try:
            with open(file_found, 'r', encoding='utf-8', errors="ignore") as f:
                data = f.read()
                for match in ascii_chars_re.findall(data):
                    if match not in unique_items:
                        out_lines.append(match)
                        unique_items.add(match)
        except Exception as e:
            logfunc(f"Error reading {file_found}: {e}")
            continue

        if unique_items:
            try:
                with open(outputpath, 'w', encoding='utf-8') as g:
                    g.write('\n'.join(out_lines) + '\n')

                out = f'<a href="{output_filename}" target="_blank" style="color:blue">{journalName}</a>'

                data_list.append((out, file_found, journalName))
                x += 1
            except OSError as e:
                logfunc(f"Error writing report file {outputpath}: {e}")

    data_headers = ('Report', 'Location', 'Filename')

    if not data_list:
        logfunc("No strings found in WAL/Journal files.")
        return data_headers, [], source_path_ref

    return data_headers, data_list, source_path_ref
