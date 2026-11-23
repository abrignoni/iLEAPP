__artifacts_v2__ = {
    "offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "MHTML and MHT files found in the extraction, with the "
                       "Snapshot-Content-Location, Subject and Date headers each file carries",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Offline Pages",
        "notes": "Timestamp Modified is the modification time the tool reads from the input for "
                 "the file as a UTC time, to the whole second, such as from a tar header or a zip"
                 " entry's NTFS or extended timestamp field. When the tool reads no UTC time, "
                 "Timestamp Modified is blank and Modified (no zone, as stored) shows the date "
                 "and time the input holds, with no zone conversion. That is the case for a FAT "
                 "directory entry, an exFAT directory entry (its stored UTC offset is not applied"
                 " or shown here) and a zip entry with only its DOS date and time. Both columns "
                 "are blank when the input holds neither, and a recorded time of 0 is treated as "
                 "no time. For a folder or single-file input Timestamp Modified is the time the "
                 "operating system reports for that file on the examiner's machine, including any"
                 " conversion it applied, and whatever copied the file there may have set it. The"
                 " staged copy's own time is not reported. Timestamp Modified depends on the "
                 "acquisition having kept file times. Web Source is the Snapshot-Content-Location"
                 " header, Subject is the Subject header and MIME Date is the Date header, each "
                 "as Python's email parser returns the first header of that name. Encoded words "
                 "are not decoded, and bytes that are not valid UTF-8 are replaced. Source "
                 "location in the extraction is provided for each item.",
        "paths": ('*/*.mhtml', '*/*.mht'),
        "output_types": "standard",
        "artifact_icon": "file-text"
    }
}

import email
import os

from datetime import datetime, timedelta, timezone
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc


def _utc(seconds):
    """Unix seconds as a UTC datetime in whole seconds, '' for none or a value datetime cannot hold."""
    if seconds is None:
        return ''
    try:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=int(seconds))
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
    for value in (getattr(times, 'modified', None), getattr(info, 'modification_date', None)):
        if isinstance(value, (int, float)) and value:
            return value, ''
    return None, getattr(times, 'modified_no_zone', None) or ''


@artifact_processor
def offlinePages(context):
    data_headers = (
        ('Timestamp Modified', 'datetime'),
        'Modified (no zone, as stored)',
        'MIME Date',
        ('File', 'media'),
        'Web Source',
        'Subject',
        'Source in Extraction')
    data_list = []
    source_dirs = set()

    for file_found in context.get_files_found():
        file_found = str(file_found)

        modified, no_zone = _file_times(context.get_seeker(), file_found)
        modified_time = _utc(modified)

        try:
            with open(file_found, 'r', errors='replace', encoding='utf-8') as fp:
                message = email.message_from_file(fp)
        except OSError as ex:
            logfunc(f'Failed to read offline page {file_found}: {ex}')
            continue

        source_dirs.add(os.path.dirname(file_found))
        media_ref = check_in_media(file_found)
        data_list.append((
            modified_time,
            no_zone,
            message['Date'],
            media_ref,
            message['Snapshot-Content-Location'],
            message['Subject'],
            context.get_relative_path(file_found)))

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
