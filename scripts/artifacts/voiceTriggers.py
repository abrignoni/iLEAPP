import json
import datetime
import shutil
from os import listdir
from os.path import isfile, join, basename

from scripts.ilapfuncs import artifact_processor


def format_time(date_time_str):
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y%m%d')
    formatted = '{}-{}-{}'.format(date_time_obj.year, date_time_obj.month, date_time_obj.day)
    return formatted


@artifact_processor
def get_voiceTriggers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    info_files = []
    data_list = []
    if len(files_found) > 1:
        for file_found in files_found:
            if file_found.endswith('wav'):
                shutil.copyfile(file_found, join(report_folder, basename(file_found)))
            elif file_found.endswith('json') and 'meta_version.json' != basename(file_found):
                info_files.append(file_found)

        info_files.sort()
        wav_files = [join(report_folder, fname) for fname in listdir(report_folder) if isfile(join(report_folder, fname))]
        wav_files.sort()

        for info_file, wav_file in zip(info_files, wav_files):
            if basename(info_file).split('.')[0] == basename(wav_file).split('.')[0]:
                with open(info_file, "rb") as f:
                    fl = json.load(f)
                    if 'grainedDate' in fl:
                        creation_date = format_time(fl['grainedDate'])
                    else:
                        creation_date = ''

                    audio = '''
                            <audio controls>
                                <source src={} type="audio/wav">
                                <p>Your browser does not support HTML5 audio elements.</p>
                            </audio>
                            '''.format(wav_file)

                    data_list.append((creation_date, fl['productType'], fl['utteranceWav'], audio))

    data_headers = ('Creation Date', 'Device', 'Path to File', 'Audio File')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_voiceTriggers": {
        "name": "Voice Triggers",
        "description": "Voice trigger audio samples with device metadata.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Voice-Triggers",
        "notes": "",
        "paths": ('**/td/audio/*.json', '**/td/audio/*.wav'),
        "output_types": "standard",
        "artifact_icon": "mic",
        "html_columns": ["Audio File"]
    }
}
