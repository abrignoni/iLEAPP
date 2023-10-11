import plistlib
from datetime import datetime
import shutil
from os import listdir
from os.path import isfile, join, basename, dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def unix_epoch_to_readable_date(unix_epoch_time):
    unix_time = float(unix_epoch_time + 978307200)
    readable_time = datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
    return readable_time


def get_voiceRecordings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    if len(files_found) > 0:
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
        m4a_files = [join(report_folder, file) for file in listdir(report_folder) if isfile(join(report_folder, file))]
        m4a_files.sort()

        for plist_file, m4a_file in zip(plist_files, m4a_files):
            with open(plist_file, "rb") as file:
                pl = plistlib.load(file)
                ct = unix_epoch_to_readable_date(pl['RCSavedRecordingCreationTime'])

                audio = ''' 
                            <audio controls>
                                <source src={} type="audio/wav">
                                <p>Your browser does not support HTML5 audio elements.</p>
                            </audio> 
                            '''.format(m4a_file)

                data_list.append((ct, pl['RCSavedRecordingTitle'], pl['RCComposedAVURL'].split('//')[1], audio))

        report = ArtifactHtmlReport('Voice Recordings')
        report.start_artifact_report(report_folder, 'Voice Recordings')
        report.add_script()
        data_headers = ('Creation Date', 'Title', 'Path to File', 'Audio File')
        report.write_artifact_data_table(data_headers, data_list, dirname(file_found), html_no_escape=['Audio File'])
        report.end_artifact_report()

        tsvname = 'Voice Recordings'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Voice Recordings'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Voice Recordings found')

    return

__artifacts__ = {
    "voiceRecordings": (
        "Voice-Recordings",
        ('**/Recordings/*.composition/manifest.plist','**/Recordings/*.m4a'),
        get_voiceRecordings)
}