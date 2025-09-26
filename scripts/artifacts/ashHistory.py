__artifacts_v2__ = {
    "AshHistory": {
        "name": "Alpine Linux Bash History",
        "description": "Extracts command history from Alpine Linux bash",
        "author": "@yourusername",
        "creation_date": "2024-10-18",
        "last_update_date": "2024-10-18",
        "requirements": "none",
        "category": "Linux",
        "notes": "",
        "paths": ('*/.ash_history',),
        "output_types": "all"
    }
}

import codecs
from scripts.ilapfuncs import artifact_processor
from scripts.context import Context

@artifact_processor
def AshHistory(context:Context):
    files_found = context.get_files_found()
    data_list = []
    file_found = str(files_found[0])
    counter = 1
    
    with codecs.open(file_found, 'r', 'utf-8-sig') as csvfile:
        for row in csvfile:
            data_list.append((counter, row.strip()))
            counter += 1
    
    data_headers = ('Sequence', 'Command')
    return data_headers, data_list, file_found
