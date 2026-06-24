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
        "artifact_icon": "database"
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
