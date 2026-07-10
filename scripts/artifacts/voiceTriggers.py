__artifacts_v2__ = {
    "voiceTriggers": {
        "name": "Voice-Triggers",
        "description": "Extracts Voice Trigger audio recordings and metadata.",
        "author": "@Anna-Mariya Mateyna",
        "creation_date": "2020-12-21",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Audio",
        "notes": "",
        "paths": ('*/Library/VoiceTrigger/SAT/*/td/audio/*.json', '*/Library/VoiceTrigger/SAT/*/td/audio/*.wav'),
        "output_types": "standard",
        "artifact_icon": "microphone",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 9 rows",
        }
    }
}

import json
import datetime
import os

from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    check_in_media
)


def format_time(date_time_str):
    try:
        return datetime.datetime.strptime(date_time_str, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)
    except (TypeError, ValueError):
        return date_time_str


@artifact_processor
def voiceTriggers(context):
    files_found = context.get_files_found()

    data_list = []
    json_files = [str(f) for f in files_found if str(f).endswith('.json') and 'meta_version.json' not in str(f)]

    for info_file in json_files:
        wav_file_path = info_file.replace('.json', '.wav')
        audio_id = None
        if os.path.exists(wav_file_path):
            audio_id = check_in_media(wav_file_path)

        try:
            with open(info_file, "rb") as file:
                fl = json.load(file)
                if 'grainedDate' in fl:
                    creation_date = format_time(fl['grainedDate'])
                else:
                    creation_date = ''

                data_list.append((
                    creation_date,
                    fl.get('productType', ''),
                    fl.get('utteranceWav', ''),
                    audio_id,
                    context.get_relative_path(info_file)
                ))

        except (OSError, TypeError, ValueError, KeyError) as e:
            logfunc(f"Error processing {info_file}: {e}")

    data_headers = (
        ('Creation Date', 'datetime'),
        'Device',
        'Internal Path Info',
        ('Audio File', 'media'),
        'Source File'
    )

    source_path = json_files[0] if json_files else ''

    return data_headers, data_list, source_path
