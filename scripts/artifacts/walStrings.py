import os
import re
import string

from pathlib import Path

from scripts.ilapfuncs import artifact_processor

control_chars = ''.join(map(chr, range(0, 32))) + ''.join(map(chr, range(127, 160)))
not_control_char_re = re.compile(f'[^{control_chars}]' + '{4,}')
# If  we only want ascii, use 'ascii_chars_re' below
printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')


@artifact_processor
def get_walStrings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    x = 1
    data_list = []
    for file_found in files_found:
        filesize = Path(file_found).stat().st_size
        if filesize == 0:
            continue

        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, str(x) + '_' + journalName + '.txt')

        level2, level1 = (os.path.split(outputpath))
        level2 = (os.path.split(level2)[1])
        final = level2 + '/' + level1

        unique_items = set()
        out_lines = []
        with open(file_found, errors="ignore", encoding="utf-8") as f:
            data = f.read()
            for match in ascii_chars_re.findall(data):
                if match not in unique_items:
                    out_lines.append(match)
                    unique_items.add(match)

        if unique_items:
            with open(outputpath, 'w', encoding="utf-8") as g:
                g.write('\n'.join(out_lines) + '\n')
            out = (f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>')
            data_list.append((out, file_found))
        else:
            try:
                os.remove(outputpath)
            except OSError:
                pass
        x = x + 1

    data_headers = ('Report', 'Location')
    return data_headers, data_list, ''

__artifacts_v2__ = {
    "get_walStrings": {
        "name": "SQLite Journal Strings",
        "description": "ASCII strings extracted from SQLite journal and WAL files.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "SQLite Journaling",
        "notes": "",
        "paths": ('**/*-wal', '**/*-journal'),
        "output_types": ["html"],
        "artifact_icon": "file-text",
        "html_columns": ["Report"]
    }
}
