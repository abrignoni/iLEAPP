import os
import re
import string

from pathlib import Path
from html import escape

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

control_chars = ''.join(map(chr, range(0,32))) + ''.join(map(chr, range(127,160)))
not_control_char_re = re.compile(f'[^{control_chars}]' + '{4,}')
# If  we only want ascii, use 'ascii_chars_re' below
printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')

def get_walStrings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    x = 1
    data_list = []
    for file_found in files_found:
        filesize = Path(file_found).stat().st_size
        if filesize == 0:
            continue

        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, str(x) + '_' + journalName + '.txt') # name of file in txt

        level2, level1 = (os.path.split(outputpath))
        level2 = (os.path.split(level2)[1])
        final = level2 + '/' + level1
        
        unique_items = set() # For deduplication of strings found
        out_lines = []
        with open(file_found, errors="ignore") as f:  # Python 3.x
            data =  f.read()
            #for match in not_control_char_re.finditer(data): # This gets all unicode chars, can include lot of garbage if you only care about English, will miss out other languages
            for match in ascii_chars_re.findall(data): # Matches ONLY Ascii (old behavior) , good if you only care about English
                if match not in unique_items:
                    out_lines.append(match)
                    unique_items.add(match)

        if unique_items:
            with open(outputpath, 'w') as g:
                g.write('\n'.join(out_lines) + '\n')
            out = (f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>')
            data_list.append((out, file_found))
        else:
            try:
                os.remove(outputpath) # delete empty file
            except OSError:
                pass
        x = x + 1

    location =''
    description = 'ASCII strings extracted from SQLite journal and WAL files.'
    report = ArtifactHtmlReport('Strings - SQLite Journal & WAL')
    report.start_artifact_report(report_folder, 'Strings - SQLite Journal & WAL', description)
    report.add_script()
    data_headers = ('Report', 'Location')
    report.write_artifact_data_table(data_headers, data_list, location, html_escape=False)
    report.end_artifact_report()

__artifacts__ = {
    "walStrings": (
        "SQLite Journaling",
        ('**/*-wal','**/*-journal'),
        get_walStrings)
}