import datetime
import email
import os

from scripts.ilapfuncs import artifact_processor, media_to_html


@artifact_processor
def get_offlinePages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)

        with open(file_found, 'r', encoding='utf-8', errors='replace') as fp:
            message = email.message_from_file(fp)
            sourced = (message['Snapshot-Content-Location'])
            subjectd = (message['Subject'])
            dated = (message['Date'])
            media = media_to_html(file_found, files_found, report_folder)

        data_list.append((utc_modified_date, media, sourced, subjectd, dated, file_found))

    data_headers = ('Timestamp Modified', 'File', 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "Saved offline web pages with metadata.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Offline Pages",
        "notes": "",
        "paths": ('*/*.mhtml', '*/*.mht'),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "html_columns": ["File"]
    }
}
