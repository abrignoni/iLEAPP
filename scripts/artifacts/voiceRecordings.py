import plistlib
from datetime import datetime
import shutil
from os import listdir
from os.path import isfile, join, basename

from scripts.ilapfuncs import artifact_processor


def unix_epoch_to_readable_date(unix_epoch_time):
    unix_time = float(unix_epoch_time + 978307200)
    readable_time = datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
    return readable_time


@artifact_processor
def get_voiceRecordings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    plist_files = []

    for file_found in files_found:
        if file_found.endswith('plist'):
            plist_files.append(file_found)
        elif file_found.endswith('m4a'):
            m4a_filename = basename(file_found)
            if ' ' in m4a_filename:
                m4a_filename = m4a_filename.replace(' ', '_')
            shutil.copyfile(file_found, join(report_folder, m4a_filename))

    plist_files.sort()
    m4a_files = [join(report_folder, fname) for fname in listdir(report_folder) if isfile(join(report_folder, fname))]
    m4a_files.sort()

    for plist_file, m4a_file in zip(plist_files, m4a_files):
        with open(plist_file, "rb") as f:
            pl = plistlib.load(f)
            ct = unix_epoch_to_readable_date(pl['RCSavedRecordingCreationTime'])

            audio = '''
                        <audio controls>
                            <source src={} type="audio/wav">
                            <p>Your browser does not support HTML5 audio elements.</p>
                        </audio>
                        '''.format(m4a_file)

            data_list.append((ct, pl['RCSavedRecordingTitle'], pl['RCComposedAVURL'].split('//')[1], audio))

    data_headers = ('Creation Date', 'Title', 'Path to File', 'Audio File')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_voiceRecordings": {
        "name": "Voice Recordings",
        "description": "Voice memo recordings with creation dates.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Voice-Recordings",
        "notes": "",
        "paths": ('**/Recordings/*.composition/manifest.plist', '**/Recordings/*.m4a'),
        "output_types": "standard",
        "artifact_icon": "mic",
        "html_columns": ["Audio File"]
    }
}
