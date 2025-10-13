__artifacts_v2__ = {
    "get_spotlightIndexCache": {
        "name": "Spotlight Index Cache V2",
        "description": "Spotlight Index Cache V2",
        "author": "@JohnHyla",
        "version": "0.0.1",
        "date": "2025-10-09",
        "requirements": "none",
        "category": "Spotlight",
        "notes": "",
        "paths": ('*/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/Cache/*/*.txt'),
        "output_types": "standard",
        "artifact_icon": "search"
    }
}

import os
import datetime
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_ts_human_to_timezone_offset

@artifact_processor
def get_spotlightIndexCache(context):

    data_list = []
    report_file = '/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/Cache/'

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        cache_folder = os.path.basename(os.path.dirname(file_found))

        with open(file_found, 'r', encoding="utf-8", errors="replace") as text_file:
            text_content = text_file.read()
            modified_time = os.path.getmtime(file_found)
            utc_modified_date = datetime.datetime.fromtimestamp(modified_time, tz=datetime.timezone.utc)


            data_list.append((utc_modified_date, text_content, cache_folder, filename))



    data_headers = (('File Modified Time', 'datetime'), 'Text Content', 'Cache Folder', 'Filename')

    return data_headers, data_list, report_file


