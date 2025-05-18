__artifacts_v2__ = {
    "logarchive": {
        "name": "logarchive",
        "description": "Processes a json file from a logarchive",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-05-06",
        "last_update_date": "2025-05-06",
        "requirements": "none",
        "category": "Logs",
        "notes": "",
        "paths": ('*/logarchive.json',),
        "output_types": "lava_only",
        "artifact_icon": "user"
    }
}

import ijson
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, logfunc

def convert_to_utc(timestamp):
    dt_local = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    dt_utc = dt_local.astimezone(timezone.utc)
    
    return(dt_utc)


def truncate_after_last_bracket(file_path):
    with open(file_path, 'rb+') as f:
        # Start from the end of the file and scan backwards
        f.seek(0, 2)  # Move to end of file
        file_size = f.tell()
        
        for i in range(file_size - 1, -1, -1):
            f.seek(i)
            char = f.read(1)
            if char == b']':
                # Truncate the file just after this bracket
                f.truncate(i + 1)
                logfunc(f"Truncated file after position {i+1}")
                return
        print("No closing bracket `]` found.")



@artifact_processor
def logarchive(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
    
    if file_found.endswith('logarchive.json'):
        truncate_after_last_bracket(file_found)
        with open(file_found, 'rb') as f:
            for record in ijson.items(f, 'item', multiple_values=True ): # if the json is a list
                if isinstance(record, dict):
                    timestamp = processid = subsystem = category = eventmessage = traceid = ''
                    
                    for key, value in record.items():
                        if key == 'timestamp':
                            value = convert_to_utc(value)
                            timestamp = value
                        elif key == 'processID':
                            processid = value
                        elif key == 'subsystem':
                            subsystem = value
                        elif key == 'category':
                            category = value
                        elif key == 'eventMessage':
                            eventmessage = str(value)
                        elif key == 'traceID':
                            traceid = value
                    #print(timestamp, processid, subsystem, category, eventmessage, traceid)
                    data_list.append((timestamp, processid, subsystem, category, eventmessage, traceid))
                else:
                    logfunc(f'Not added:{record}')
    
    data_headers = (('Timestamp', 'datetime'), 'Process ID', 'Subsystem', 'Category', 'Event Message, Trace ID')
    return data_headers, data_list, file_found