__artifacts_v2__ = {
    "kikPendingUploads": {
        "name": "Kik Pending Uploads",
        "description": "Metadata from the Kik chunked_upload_storage pending_uploads bplist, with the pending media file",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/cores/private/*/chunked_upload_storage/pending_uploads',
            '*/mobile/Containers/Shared/AppGroup/*/cores/private/*/chunked_upload_storage/data_cache/*',
        ),
        "output_types": "standard",
        "artifact_icon": "upload",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | Kik Messaging & Chat App 17.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Kik Messaging & Chat App 16.9.3 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Kik Messaging & Chat App 17.11.3 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Kik Messaging & Chat App 16.16.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | Kik Messaging & Chat App 16.9.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Kik 15.21.2 | 1 row",
            "hickman_ios14": "iOS 14.3 | Kik 15.25.1 | 1 row",
        }
    }
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media


@artifact_processor
def kikPendingUploads(context):
    data_headers = ('Upload Start Time', 'App ID', 'Content ID', 'Progress', 'Retries Remaining',
                    'State', ('Pending File', 'media'))
    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('pending_uploads'):
            continue
        source_path = source_path or file_found

        try:
            root = ET.parse(file_found).getroot()
        except ET.ParseError:
            continue

        # The plist stores alternating key/value text nodes; rebuild the dict.
        a_dict = {}
        counter = 0
        key = ''
        for elem in root:
            for subelem in elem:
                for subelem2 in subelem:
                    if counter == 0:
                        key = subelem2.text
                        a_dict[key] = ''
                        counter = 1
                    else:
                        a_dict[key] = subelem2.text
                        counter = 0

        content_id = a_dict.get('contentID', '')
        media = ''
        if content_id:
            for match in context.get_files_found():
                match = str(match)
                if content_id in match and os.path.isfile(match):
                    media = check_in_media(match) or ''
                    break

        data_list.append((a_dict.get('uploadStartTime', ''), a_dict.get('appID', ''), content_id,
                          a_dict.get('progress', ''), a_dict.get('retriesRemaining', ''),
                          a_dict.get('state', ''), media))

    return data_headers, data_list, source_path
