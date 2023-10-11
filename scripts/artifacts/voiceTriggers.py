import json
import datetime
import shutil
from os import listdir
from os.path import isfile, join, basename, dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def format_time(date_time_str):
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y%m%d')
    formatted = '{}-{}-{}'.format(date_time_obj.year, date_time_obj.month, date_time_obj.day)
    return formatted


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
        wav_files = [join(report_folder, file) for file in listdir(report_folder) if isfile(join(report_folder, file))]
        wav_files.sort()

        for info_file, wav_file in zip(info_files, wav_files):
            if basename(info_file).split('.')[0] == basename(wav_file).split('.')[0]:
                with open(info_file, "rb") as file:
                    fl = json.load(file)
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

        report = ArtifactHtmlReport('Voice Triggers')
        report.start_artifact_report(report_folder, 'Voice Triggers')
        report.add_script()
        data_headers = ('Creation Date', 'Device', 'Path to File', 'Audio File')
        report.write_artifact_data_table(data_headers, data_list, dirname(file_found), html_no_escape=['Audio File'])
        report.end_artifact_report()

        tsvname = 'Voice Triggers'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Voice Triggers'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Voice Triggers found')

    return

__artifacts__ = {
    "voiceTriggers": (
        "Voice-Triggers",
        ('**/td/audio/*.json','**/td/audio/*.wav'),
        get_voiceTriggers)
}