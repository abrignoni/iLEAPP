__artifacts_v2__ = {
    "AshHistory": {
        "name": "Ash Shell History",
        "description": "Extracts command history from an ash shell history file (.ash_history)",
        "author": "James Habben",
        "creation_date": "2023-05-24",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Linux",
        "notes": "",
        "paths": ('*/.ash_history',),
        "output_types": "all",
        "artifact_icon": "terminal"
    }
}

import codecs
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def AshHistory(context):
    data_list = []
    files_found = context.get_files_found()
    file_found = str(files_found[0])
    counter = 1
    
    with codecs.open(file_found, 'r', 'utf-8-sig') as csvfile:
        for row in csvfile:
            data_list.append((counter, row.strip()))
            counter += 1
    
    data_headers = ('Sequence', 'Command')
    return data_headers, data_list, file_found
