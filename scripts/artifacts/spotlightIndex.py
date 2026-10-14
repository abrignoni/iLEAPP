__artifacts_v2__ = {
    "get_spotlightIndexCache": {
        "name": "Spotlight Index Cache V2",
        "description": "Text content of the CoreSpotlight index.spotlightV2 cache text files, "
                       "with the cache folder, the file name and the modified time of the "
                       "tool's staged copy of each file.",
        "author": '@snoop168, @AlexisBrignoni, Codex',
        "creation_date": "2025-10-09",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Spotlight",
        "notes": "Staged Copy mtime is the numeric modification time of the copy the tool staged, "
                 "reported as text without an asserted evidence time zone. It is not read from a record inside the evidence. For a zip "
                 "extraction the tool sets that time from the zip entry's date and time, which "
                 "has no time zone and is read in the local zone of the machine that ran the tool.",
        "paths": ('*/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/Cache/*/*.txt'),
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
from scripts.ilapfuncs import artifact_processor

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
            modified_time = os.path.getmtime(file_found)
            staged_modified = str(modified_time)


            data_list.append((staged_modified, text_content, cache_folder, filename))



    data_headers = ('Staged Copy mtime (seconds as stored)', 'Text Content', 'Cache Folder', 'Filename')

    return data_headers, data_list, '\n'.join(sorted(source_paths))


