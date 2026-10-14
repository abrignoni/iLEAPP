__artifacts_v2__ = {
    "get_draftmessage": {
        "name": "Draft Native Messages",
        "description": "Draft text from SMS/Drafts/<chat>/composition.plist files, with the chat "
                       "folder name and the modified time of each plist file as extracted. The "
                       "time is file system metadata, not a value stored in the draft.",
        "author": "@abrignoni",
        "creation_date": "2022-10-18",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Messages",
        "notes": "Modified Time is the modification time of the composition.plist file as staged "
                 "for this run. Draft Message is the NSString of the plist's text value. Files "
                 "whose path contains 'tombstone' are skipped.",
        "paths": ('*/SMS/Drafts/*/composition.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

import os
import nska_deserialize as nd
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_plist_file_content

@artifact_processor
def get_draftmessage(context):
    data_list = []
    source_dirs = set()
    data_headers = (('Modified Time', 'datetime'),'Chat Directory Name','Draft Message', 'Source file')
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found) #reusing old code and adding new underneath. I know. "Cringe."
        path = Path(file_found)
        directoryname = (path.parent.name)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
            else:
                pass
        else:
            continue
    
        source_dirs.add(os.path.dirname(file_found))
        modifiedtime = convert_unix_ts_to_utc(os.path.getmtime(file_found))
        
        pl = get_plist_file_content(file_found)
        deserialized_plist = nd.deserialize_plist_from_string(pl['text'])
        data_list.append((modifiedtime, directoryname, deserialized_plist.get('NSString', ''), context.get_relative_path(file_found)))
    
    return data_headers, data_list, '\n'.join(sorted(source_dirs))