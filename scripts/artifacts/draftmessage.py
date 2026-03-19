__artifacts_v2__ = {
    "get_draftmessage": {  # This should match the function name exactly
        "name": "Draft Native Messages",
        "description": "",
        "author": "",
        "creation_date": "",
        "last_updated": "2025-11-25",
        "requirements": "none",
        "category": "Messages",
        "notes": "",
        "paths": ('*/SMS/Drafts/*/composition.plist'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-circle"
    }
}

import os
import nska_deserialize as nd
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_in_seconds, get_plist_file_content

@artifact_processor
def get_draftmessage(context):
    data_list = []
    data_headers = (('Modified Time', 'datetime'),'Intended Recipient','Draft Message', 'Source file')
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found) #reusing old code and adding new underneath. I know. "Cringe."
        path = Path(file_found)
        directoryname = (path.parent.name)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                pass
        else:
            continue
    
        modifiedtime = os.path.getmtime(file_found)
        modifiedtime = convert_unix_ts_in_seconds(modifiedtime)
        
        pl = get_plist_file_content(file_found)
        deserialized_plist = nd.deserialize_plist_from_string(pl['text'])
        data_list.append((modifiedtime, directoryname, deserialized_plist.get('NSString', ''), file_found))
    
    return data_headers, data_list, 'see Source File for more info'