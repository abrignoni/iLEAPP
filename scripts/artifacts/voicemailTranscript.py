__artifacts_v2__ = {
    "get_voicemail_transcript": {
        "name": "Voicemail Transcript",
        "description": "Parses Voicemail Transcript Files",
        "author": "@JohnHyla",
        "version": "0.0.1",
        "date": "2025-04-11",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": (
            '*/private/var/mobile/Library/Voicemail/*.transcript',
            '*/private/var/mobile/Library/Application Support/com.apple.FaceTime/Assets/*.transcript'
        ),
        "output_types": "standard"
    }
}

import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor
import datetime

@artifact_processor
def get_voicemail_transcript(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        with open(file_found, 'rb') as f:
            deserialized_plist = nd.deserialize_plist(f)

        data_list.append([
            datetime.datetime.utcfromtimestamp(seeker.file_infos[file_found].creation_date),
            datetime.datetime.utcfromtimestamp(seeker.file_infos[file_found].modification_date),
            seeker.file_infos[file_found].source_path,
            deserialized_plist['transcriptionString'],
            deserialized_plist['confidence']])

    data_headers = ('File Created', 'File Modified', 'Filename', 'Transcript', 'Confidence')

    return data_headers, data_list, 'See Filename Column'
