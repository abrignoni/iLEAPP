""" Photos picker client log: PhotoData/Caches/PhotosPickerLogs/<bundle identifier> """
__artifacts_v2__ = {
    "photosPickerLog": {
        "name": "Photos Picker Log",
        "description": "One row per app with a Photos picker client log file: the app's bundle identifier and "
                       "the time stored under the key Apple names the presented timestamp, shown in UTC.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Photos",
        "notes": "A row is one file in PhotoData/Caches/PhotosPickerLogs. In the 54 files read, each file is a "
                 "property list named with the bundle identifier it holds, so there is one file and one row per "
                 "app, and a file holds one "
                 "time; whether that time is the first or the latest presentation for the app is not established. "
                 "The key meanings are from the names PhotoLibraryServicesCore exports for them, read on macOS "
                 "27.0.1 (26A434) and not exercised on iOS: timestamp is PLPhotosPickerLogPresentedTimestampKey, "
                 "bundleIdentifier is PLPhotosPickerLogClientBundleIdentifierKey and pickerUsesOptions is "
                 "PLPhotosPickerLogPickerUsesOptionsKey. The key name says the picker was presented to the app at "
                 "that time; the code that writes the file was not read, so that meaning rests on the name alone. "
                 "A row does not show that any photo or video was chosen or shared. Picker "
                 "Presented is stored either as text with milliseconds and a UTC offset (format yyyy-MM-dd "
                 "HH:mm:ss.SSSZZZZZ, a format string found 20 strings after pickerUsesOptions in the macOS shared "
                 "cache; the pairing is by proximity only, and every text value read parsed with it), read with "
                 "that offset, or as a "
                 "plist date read as UTC. Both forms were found, on 47 and 7 of the 54 files, and on dexter_ios18,"
                 " hc_ios18_7, hc_ios26 and iphone12_ios18 both sat in one folder. Stored UTC Offset is the offset"
                 " in the text form and is blank on rows stored as a plist date. Picker Uses Options is the stored"
                 " boolean, blank when the file has no such key (25 of 54); what it records is not established. "
                 "The 10 images with picker log files held 1 to 15 each. The other 8 images in sample_data have no"
                 " PhotosPickerLogs file, which is not evidence the picker was never used.",
        "paths": ('*/PhotoData/Caches/PhotosPickerLogs/*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "image",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 2 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "hc_ios17_2": "iOS 17.2.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 11 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 12 rows",
            "iphone11_ios17": "iOS 17.3 | 15 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
        },
    },
}

import hashlib
import os
import plistlib
from datetime import datetime, timezone
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc

_ERRORS = (OSError, plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError)
# The string form, read with its stored offset: yyyy-MM-dd HH:mm:ss.SSSZZZZZ
_STRING_FORMAT = '%Y-%m-%d %H:%M:%S.%f%z'


def _presented(value, source):
    '''(aware UTC datetime or None, stored UTC offset text) for the stored timestamp.'''
    if isinstance(value, datetime):
        # plistlib returns a <date> as a naive datetime that is already UTC
        when = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
        return when, ''
    if isinstance(value, str):
        try:
            stored = datetime.strptime(value, _STRING_FORMAT)
        except ValueError:
            logfunc(f'Photos Picker Log: {source} timestamp is text that did not read as a time')
            return None, ''
        offset = stored.strftime('%z')
        return stored.astimezone(timezone.utc), f'{offset[:3]}:{offset[3:]}'
    if value is not None:
        logfunc(f'Photos Picker Log: {source} timestamp is a {type(value).__name__}, not a time')
    return None, ''


@artifact_processor
def photosPickerLog(context):
    """ See artifact description """
    data_headers = (('Picker Presented (UTC)', 'datetime'), 'Client Bundle Identifier', 'Stored UTC Offset',
                    'Picker Uses Options (as stored)')
    data_list = []
    seen = {}
    for file_found in sorted(str(f) for f in context.get_files_found()):
        name = os.path.basename(file_found)
        if name.startswith('._') or not os.path.isfile(file_found):
            continue
        try:
            with open(file_found, 'rb') as handle:
                data = handle.read()
            log = plistlib.loads(data)
        except _ERRORS as ex:
            logfunc(f'Photos Picker Log: {file_found} not read as a property list: {ex}')
            continue
        if not isinstance(log, dict):
            logfunc(f'Photos Picker Log: {file_found} is not a dictionary')
            continue
        # the same file can be reached through two views of one extraction; read identical bytes once
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            logfunc(f'Photos Picker Log: {file_found} is byte-identical to {seen[digest]}, read once')
            continue
        seen[digest] = file_found
        when, offset = _presented(log.get('timestamp'), file_found)
        uses_options = log.get('pickerUsesOptions')
        data_list.append((when, str(log.get('bundleIdentifier', '')), offset,
                          '' if uses_options is None else str(uses_options)))
    return data_headers, data_list, '\n'.join(seen.values())
