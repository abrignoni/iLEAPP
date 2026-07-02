__artifacts_v2__ = {
    "get_obliterated": {
        "name": "Obliterated Time",
        "description": "Parses obliterated timestamp",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/root/.obliterated'),
        "output_types": "standard",
        "artifact_icon": "trash",
    }
}

import datetime
from datetime import timezone
import os
from scripts.ilapfuncs import logdevinfo, artifact_processor

@artifact_processor
def get_obliterated(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    file_found = str(files_found[0])
    
    modified_time = os.path.getmtime(file_found)
    utc_modified_date = datetime.datetime.fromtimestamp(modified_time, tz=timezone.utc)
    
    logdevinfo(f'<b>Obliterated Timestamp: </b>{utc_modified_date}')
    
    data_list = [(utc_modified_date,)]

    data_headers = (('Timestamp', 'datetime'), )

    return data_headers, data_list, file_found