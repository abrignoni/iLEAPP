import os
import textwrap
import datetime
import sys
import re
import string
from html import escape

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def strings(filename, min=4):
    with open(filename, errors="ignore") as f:  # Python 3.x
    # with open(filename, "rb") as f:           # Python 2.x
        result = ""
        for c in f.read():
            if c in string.printable:
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""
        if len(result) >= min:  # catch result at EOF
            yield result

def get_journalStrings(files_found, report_folder, seeker):
    x = 0
    data_list =[]
    for file_found in files_found:
        x = x + 1
        sx = str(x)
        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, sx+'_'+journalName+'.txt') # name of file in txt
        #linkpath = os.path.basename(
        level2, level1 = (os.path.split(outputpath))
        level2 = (os.path.split(level2)[1])
        final = level2+'/'+level1
        with open(outputpath, 'w') as g:
            for s in strings(file_found):
                g.write(s)
                g.write('\n')
        
        out = (f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>') 
        
        data_list.append((out, file_found))

    location =''
    description = 'ASCII and Unicode strings extracted from SQLite journaing files.'
    report = ArtifactHtmlReport('Strings - SQLite Journal')
    report.start_artifact_report(report_folder, 'Strings - SQLite Journal', description)
    report.add_script()
    data_headers = ('Report', 'Location')
    report.write_artifact_data_table(data_headers, data_list, location, html_escape=False)
    report.end_artifact_report()

  