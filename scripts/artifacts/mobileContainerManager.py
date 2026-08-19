__artifacts_v2__ = {
    "mobileContainerManager": {
        "name": "Mobile Container Manager",
        "description": "Group container removals logged by containermanagerd",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Mobile Container Manager",
        "notes": "Two log phrasings are matched. 'Removing group container [id]' from "
                 "MCMGroupManager _cleanupUnreferencedGroupContainers... is observed on the iOS 15 "
                 "test image. 'Last reference to group container' from MCMGroupManager "
                 "_removeGroupContainersIfNeeded... appears in no local corpus log (iOS 12-17) and "
                 "is kept for older logs (unexercised path). These logs rotate and mostly hold "
                 "boot-time chatter, so most captures contain no removal lines at all.",
        "paths": ('**/containermanagerd*.log.*',),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "belkactf6": "iOS 16.3 | 0 rows (run against the decrypted filesystem copy)",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
        }
    }
}

import re
from datetime import datetime

from scripts.ilapfuncs import artifact_processor

# iOS <= 12-era phrasing; kept for older logs, not seen in the local corpus.
_MARKER_LAST_REF = ('[MCMGroupManager _removeGroupContainersIfNeededforUser:groupContainerClass:identifiers:'
                    'referenceCounts:]: Last reference to group container')

# Observed on the iOS 15 test image:
# ... -[MCMGroupManager _cleanupUnreferencedGroupContainersForUserIdentity:...]:
#     Removing group container [group.com.apple.Maps] for <501/...> at <MCMContainerPath: ...>
_REMOVING_RE = re.compile(r'Removing group container \[([^\]]+)\]')


def _line_datetime(txts):
    '''Datetime from the log prefix: <dow> <Mon> <day> <HH:MM:SS> <year>.'''
    month_number = datetime.strptime(txts[1], '%b').month
    return datetime.strptime(f'{txts[4]}-{month_number}-{txts[2]} {txts[3]}',
                             '%Y-%m-%d %H:%M:%S')


@artifact_processor
def mobileContainerManager(context):
    data_headers = (('Datetime', 'datetime'), 'Removed', 'Line', 'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        rel_path = context.get_relative_path(file_found)
        sources.append(rel_path)
        try:
            with open(file_found, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
        except OSError:
            continue

        for linecount, line in enumerate(lines, 1):
            group = None
            if _MARKER_LAST_REF in line:
                txts = line.split()
                try:
                    # group id at index 15 in this phrasing
                    group = txts[15]
                except IndexError:
                    continue
            else:
                match = _REMOVING_RE.search(line)
                if match:
                    group = match.group(1)
            if group is None:
                continue
            try:
                dtime_obj = _line_datetime(line.split())
            except (ValueError, IndexError):
                continue
            data_list.append((dtime_obj, group, linecount, rel_path))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
