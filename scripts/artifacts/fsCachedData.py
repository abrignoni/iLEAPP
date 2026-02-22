import os
import datetime

from scripts.filetype import guess_mime
from scripts.ilapfuncs import artifact_processor, media_to_html


@artifact_processor
def get_fsCachedData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        filename = os.path.basename(file_found)

        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)

        if os.path.isfile(file_found):
            mime = guess_mime(file_found)
            media = media_to_html(file_found, files_found, report_folder)
            data_list.append((utc_modified_date, media, mime, filename, file_found))

    data_headers = ('Timestamp Modified', 'Media', 'Mime Type', 'Filename', 'Path')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_fsCachedData": {
        "name": "Cache Data",
        "description": "Cached media files with timestamps and MIME types.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Cache Data",
        "notes": "",
        "paths": ('*/fsCachedData/**',),
        "output_types": "standard",
        "artifact_icon": "hard-drive",
        "html_columns": ["Media"]
    }
}
