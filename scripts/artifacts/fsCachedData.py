__artifacts_v2__ = {
    "fsCachedData": {
        "name": "fsCachedData",
        "description": "Media and other files cached under fsCachedData",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Cache Data",
        "notes": "Source location in the extraction is provided for each item.",
        "paths": ('*/fsCachedData/**',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2746 rows",
            "dexter_ios18": "iOS 18.3.2 | 1708 rows",
            "felix_ios17": "iOS 17.6.1 | 872 rows",
            "fsfull002_ios17": "iOS 17.1 | 298 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2754 rows",
            "iphone11_ios17": "iOS 17.3 | 3900 rows",
            "iphone12_ios18": "iOS 18.7 | 915 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1101 rows",
            "otto_ios17": "iOS 17.5.1 | 3221 rows",
            "abe_ios16": "iOS 16.5 | 4937 rows",
            "felix23_ios16": "iOS 16.5 | 1056 rows",
            "hickman_ios13": "iOS 13.3.1 | 1056 rows",
            "hickman_ios14": "iOS 14.3 | 1991 rows",
            "jess_ios15": "iOS 15.0.2 | 1138 rows",
            "magnet_ios16": "iOS 16.1.1 | 1037 rows",
        }
    }
}

import os

from scripts.filetype import guess_mime
from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc


@artifact_processor
def fsCachedData(context):
    data_headers = (
        ('Timestamp Modified', 'datetime'),
        ('Media', 'media'),
        'Mime Type',
        'Filename',
        'Path')
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue

        modified_time = convert_unix_ts_to_utc(os.path.getmtime(file_found))
        mime = guess_mime(file_found)
        media_ref = check_in_media(file_found)
        data_list.append((
            modified_time,
            media_ref,
            mime,
            os.path.basename(file_found),
            context.get_relative_path(file_found)))

    return data_headers, data_list, ''
