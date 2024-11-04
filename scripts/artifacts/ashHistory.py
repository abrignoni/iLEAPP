__artifacts_v2__ = {
    "AshHistory": {
        "name": "Alpine Linux Bash History",
        "description": "Extracts command history from Alpine Linux bash",
        "author": "@yourusername",
        "version": "1.0",
        "date": "2023-05-24",
        "requirements": "none",
        "category": "Linux",
        "notes": "",
        "paths": ('*/.ash_history',),
        "output_types": "all"
    }
}

import codecs
from scripts.ilapfuncs import logfunc, artifact_processor

@artifact_processor
def AshHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    counter = 1
    
    with codecs.open(file_found, 'r', 'utf-8-sig') as csvfile:
        for row in csvfile:
            data_list.append((counter, row.strip()))
            counter += 1
    
    if len(data_list) == 0:
        logfunc('No Alpine Linux Bash History file available')
        return
    
    data_headers = ('Sequence', 'Command')
    return data_headers, data_list, file_found
