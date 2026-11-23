__artifacts_v2__ = {
    "get_draftmessage": {
        "name": "Draft Native Messages",
        "description": "Draft text from SMS/Drafts/<chat>/composition.plist files, with the chat "
                       "folder name and the modified time the tool reads from the input for each "
                       "plist file. The time is file metadata from the input, not a value stored "
                       "in the draft.",
        "author": "@abrignoni",
        "creation_date": "2022-10-18",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Messages",
        "notes": "Modified Time is the modification time the tool reads from the input for the "
                 "file as a UTC time, to the whole second, such as from a tar header or a zip "
                 "entry's NTFS or extended timestamp field. When the tool reads no UTC time, "
                 "Modified Time is blank and Modified (no zone, as stored) shows the date and "
                 "time the input holds, with no zone conversion. That is the case for a FAT "
                 "directory entry, an exFAT directory entry (its stored UTC offset is not applied"
                 " or shown here) and a zip entry with only its DOS date and time. Both columns "
                 "are blank when the input holds neither, and a recorded time of 0 is treated as "
                 "no time. For a folder or single-file input Modified Time is the time the "
                 "operating system reports for that file on the examiner's machine, including any"
                 " conversion it applied, and whatever copied the file there may have set it. The"
                 " staged copy's own time is not reported. Draft Message is the NSString of the "
                 "plist's text value. Files whose path contains 'tombstone' are skipped.",
        "paths": ('*/SMS/Drafts/*/composition.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

import os
import nska_deserialize as nd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

def _utc(seconds):
    """Unix seconds as a UTC datetime in whole seconds, '' for none or a value datetime cannot hold."""
    if seconds is None:
        return ''
    try:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds // 1)
    except OverflowError:
        return ''


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if isinstance(modified, (int, float)) and modified:
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if isinstance(modified, (int, float)) and modified:
        return modified, ''
    return None, ''


@artifact_processor
def get_draftmessage(context):
    data_list = []
    source_dirs = set()
    data_headers = (('Modified Time', 'datetime'), 'Modified (no zone, as stored)', 'Chat Directory Name','Draft Message', 'Source file')
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
        modified, no_zone = _file_times(context.get_seeker(), file_found)
        modifiedtime = _utc(modified)
        
        pl = get_plist_file_content(file_found)
        deserialized_plist = nd.deserialize_plist_from_string(pl['text'])
        data_list.append((modifiedtime, no_zone, directoryname, deserialized_plist.get('NSString', ''), context.get_relative_path(file_found)))
    
    return data_headers, data_list, '\n'.join(sorted(source_dirs))