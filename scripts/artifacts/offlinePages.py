__artifacts_v2__ = {
    "offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "Saved offline web pages (MHTML/MHT) with their captured source URL and date",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Offline Pages",
        "notes": "Source location in the extraction is provided for each item.",
        "paths": ('*/*.mhtml', '*/*.mht'),
        "output_types": "standard",
        "artifact_icon": "file-text"
    }
}

import email
import os

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc


@artifact_processor
def offlinePages(context):
    data_headers = (
        ('Timestamp Modified', 'datetime'),
        ('File', 'media'),
        'Web Source',
        'Subject',
        'MIME Date',
        'Source in Extraction')
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)

        modified_time = convert_unix_ts_to_utc(os.path.getmtime(file_found))

        try:
            with open(file_found, 'r', errors='replace', encoding='utf-8') as fp:
                message = email.message_from_file(fp)
        except OSError as ex:
            logfunc(f'Failed to read offline page {file_found}: {ex}')
            continue

        media_ref = check_in_media(file_found)
        data_list.append((
            modified_time,
            media_ref,
            message['Snapshot-Content-Location'],
            message['Subject'],
            message['Date'],
            context.get_relative_path(file_found)))

    return data_headers, data_list, ''
