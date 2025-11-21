__artifacts_v2__ = {
    "get_voiceRecordings": {
        "name": "Voice Recordings",
        "description": "Extracts Voice Memo recordings and metadata.",
        "author": "@Anna-Mariya Mateyna",
        "creation_date": "2020-12-21",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Audio",
        "notes": "",
        "paths": (
            '*/Recordings/*.composition/manifest.plist',
            '*/Recordings/*.m4a'
            ),
        "output_types": "standard",
        "artifact_icon": "mic"
    }   
}

import os
from scripts.ilapfuncs import (
    logfunc,
    artifact_processor,
    get_plist_file_content,
    check_in_media,
    convert_cocoa_core_data_ts_to_utc
)


@artifact_processor
def get_voiceRecordings(context):
    files_found = context.get_files_found()
    data_list = []
    plist_files = [str(f) for f in files_found if str(f).endswith('manifest.plist')]

    audio_files_map = {os.path.basename(str(f)): str(f) for f in files_found if str(f).endswith('.m4a')}

    for plist_path in plist_files:
        try:
            pl = get_plist_file_content(plist_path)
            if not pl:
                continue

            creation_time = convert_cocoa_core_data_ts_to_utc(pl.get('RCSavedRecordingCreationTime'))
            title = pl.get('RCSavedRecordingTitle', 'No Title')
            internal_path = pl.get('RCComposedAVURL', '')

            composition_folder_name = os.path.basename(os.path.dirname(plist_path))
            expected_audio_name = composition_folder_name.replace('.composition', '.m4a')

            audio_id = None

            if expected_audio_name in audio_files_map:
                real_audio_path = audio_files_map[expected_audio_name]

                audio_id = check_in_media(real_audio_path)
            else:
                internal_audio_path = os.path.join(os.path.dirname(plist_path), expected_audio_name)
                if os.path.exists(internal_audio_path):
                     audio_id = check_in_media(internal_audio_path)

            data_list.append((
                creation_time,
                title,
                internal_path,
                audio_id,
                plist_path
            ))

        except Exception as e:
            logfunc(f"Error processing {plist_path}: {e}")

    data_headers = (
        ('Creation Date', 'datetime'),
        'Title',
        'Internal Path Info',
        ('Audio File', 'media'),
        'File Name'
    )

    source_path = plist_files[0] if plist_files else ''

    return data_headers, data_list, source_path
