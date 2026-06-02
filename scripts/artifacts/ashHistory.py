__artifacts_v2__ = {
    "AshHistory": {
        "name": "Alpine Linux Bash History",
        "description": "Extracts command history from Alpine Linux bash",
        "author": "James Habben",
        "creation_date": "2023-05-24",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Linux",
        "notes": "",
        "paths": ('*/.ash_history',),
        "output_types": "all"
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
