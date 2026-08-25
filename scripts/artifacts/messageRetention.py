# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    "messageRetention": {
        "name": "iOS Message Retention",
        "description": "Extract how long messages are kept on the device",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "version": "0.5",
        "date": "2023-10-04",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "iOS <=16 / iOS 17+ key naming per tested corpora. This directory can hold com.apple.MobileSMS.plist and com.apple.mobileSMS.plist as two different files; 6 of 20 tested images carry both, iOS 14.3 through 26.5.2. Every found file is read and each row's Setting names the source spelling it was read from. Where the report folder is on a case-insensitive volume, the file seeker preserves the second copy under a name tagged ~case- and the row's path points at the copy holding the bytes it reports; the run log records which source each tagged copy came from. On all 6 of those images the lowercase-spelled file held the same three IMDCKBackupController* keys and no retention key, so it is reported as 'No value'. Row counts are from runs on macOS. A directory input sitting on a case-insensitive volume holds only the single file that extraction kept, so both spellings can only arrive from archive or case-sensitive inputs. Reference: Apple Support, 'Delete messages and attachments', https://support.apple.com/guide/iphone/delete-messages-and-attachments-iph2c9c4bfcb/ios",
        "paths": ('*/mobile/Library/Preferences/com.apple.[Mm]obileSMS.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 3 rows; both spellings present",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 3 rows; both spellings present",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows; both spellings present",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows; both spellings present",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows; both spellings present",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 3 rows; both spellings present",
        }
    }
}

from datetime import datetime
import os
from scripts.ilapfuncs import artifact_processor, get_plist_file_content, device_info

# Values observed in tested corpora. Anything else is reported as stored.
_KEEP_VALUES = {0: 'Forever', 365: '1 Year', 30: '30 Days'}

# The key Apple uses changed between generations; both are read.
_KEEP_KEYS = (('KeepMessageForDays', 'iOS <=16'), ('SSKeepMessages', 'iOS 17+'))


def _describe(val):
    """Retention value as text. Anything unrecognized is reported as stored."""
    # dict.get would raise on an unhashable value, so only look up what can be a key.
    if isinstance(val, int):
        label = _KEEP_VALUES.get(val)
        if label:
            return label
    return f'Unrecognized value: {val}'


@artifact_processor
def messageRetention(context):
    seeker = context.get_seeker()
    data_headers = ('Setting', 'Data Value', 'Path')
    data_list = []

    # One bracket class in paths, never one pattern per spelling. os.path.normcase
    # folds case on Windows, so two case-variant patterns compile to the same thing.
    #
    # Both spellings can be present at once. iOS APFS is case-sensitive and 6 of the
    # 20 tested images carry com.apple.MobileSMS.plist and com.apple.mobileSMS.plist
    # here as different files. The seeker preserves case-variant copies under
    # distinct destination names, so every found file is read directly; each row
    # labels the source spelling and its path points at the copy holding the bytes
    # that produced it.
    source_paths = set()
    for source_path in sorted({str(p) for p in context.get_files_found()}):
        info = seeker.file_infos.get(source_path)
        filename = os.path.basename(info.source_path) if info else \
            os.path.basename(source_path)
        source_paths.add(source_path)
        rel_path = context.get_relative_path(source_path)
        pl = get_plist_file_content(source_path)

        found = False
        for key, generation in _KEEP_KEYS:
            if key not in pl:
                continue
            keep_val = _describe(pl[key])
            setting = f'{filename} - Keep Messages for Days ({generation})'
            data_list.append((setting, keep_val, rel_path))
            device_info('Messages Settings', setting, keep_val, source_path)
            found = True

        if not found:
            setting = f'{filename} - Keep Messages for Days'
            data_list.append((setting, 'No value', rel_path))
            device_info('Messages Settings', setting, 'No value', source_path)

    return data_headers, data_list, '\n'.join(sorted(source_paths))
