__artifacts_v2__ = {
    "get_voiceTriggers": {
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
        "artifact_icon": "mic"
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
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y%m%d')
        formatted = '{}-{}-{}'.format(date_time_obj.year, date_time_obj.month, date_time_obj.day)
        return formatted
    except ValueError:
        return date_time_str


@artifact_processor
def get_voiceTriggers(context):
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
                    info_file
                ))

        except Exception as e:
            logfunc(f"Error processing {info_file}: {e}")

    data_headers = (
        'Creation Date',
        'Device',
        'Internal Path Info',
        ('Audio File', 'media')
    )

    source_path = json_files[0] if json_files else ''

    return data_headers, data_list, source_path
