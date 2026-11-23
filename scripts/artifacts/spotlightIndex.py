__artifacts_v2__ = {
    "get_spotlightIndexCache": {
        "name": "Spotlight Index Cache V2",
        "description": "Text content of the CoreSpotlight index.spotlightV2 cache text files, "
                       "with the cache folder, the file name and the modified time the tool reads"
                       " from the input for each file.",
        "author": '@snoop168, @AlexisBrignoni, Codex',
        "creation_date": "2025-10-09",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Spotlight",
        "notes": "File Modified is the modification time the tool reads from the input for the "
                 "file as a UTC time, to the whole second, such as from a tar header or a zip "
                 "entry's NTFS or extended timestamp field. When the tool reads no UTC time, File"
                 " Modified is blank and Modified (no zone, as stored) shows the date and time "
                 "the input holds, with no zone conversion. That is the case for a FAT directory "
                 "entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry with only its DOS date and time. Both columns are blank "
                 "when the input holds neither, and a recorded time of 0 is treated as no time. "
                 "For a folder or single-file input File Modified is the time the operating "
                 "system reports for that file on the examiner's machine, including any "
                 "conversion it applied, and whatever copied the file there may have set it. The "
                 "staged copy's own time is not reported. File Modified is not read from the "
                 "content of the cache file. A raw image of the Data volume alone is expected to "
                 "have mobile/ at its root, with no var folder in the path; the pattern without "
                 "var/ is there to match that layout. It was checked against an extraction's path"
                 " listing with private/var removed, not on a raw image.",
        "paths": ('*/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/Cache/*/*.txt',
                  '*/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/Cache/*/*.txt'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 468 rows",
            "hc_ios18_7": "iOS 18.7.8 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | 126 rows",
        }
    }
}

import os
from datetime import datetime, timedelta, timezone
from scripts.ilapfuncs import artifact_processor

def _utc(seconds):
    """Unix seconds as a UTC datetime in whole seconds, '' for none or a value datetime cannot hold."""
    if seconds is None:
        return ''
    try:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds // 1)
    except (OverflowError, ValueError):
        return ''


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


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
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


@artifact_processor
def get_spotlightIndexCache(context):

    data_list = []
    source_paths = set()

    for file_found in context.get_files_found():
        file_found = str(file_found)
        source_paths.add(file_found)
        filename = os.path.basename(file_found)
        cache_folder = os.path.basename(os.path.dirname(file_found))

        with open(file_found, 'r', encoding="utf-8", errors="replace") as text_file:
            text_content = text_file.read()
            modified, no_zone = _file_times(context.get_seeker(), file_found)
            modified_time = _utc(modified)


            data_list.append((modified_time, no_zone, text_content, cache_folder, filename))



    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', 'Text Content', 'Cache Folder', 'Filename')

    return data_headers, data_list, '\n'.join(sorted(source_paths))


