# Module Description: Parses and extract Voicemail
# Author: @JohannPLW
# Date: 2023-10-01
# Artifact version: 0.0.2
# Requirements: none

import shutil

from os import mkdir
from os.path import join, basename, dirname
from re import search
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_voicemail(files_found, report_folder, seeker, wrap_text):
    artifact_name = 'Voicemail'
    new_report_folder = join(report_folder[:-12], artifact_name)
    voicemail_db = ''    
    if len(files_found) > 0:
        if next((True for file in files_found if 'amr' in file), False):
            mkdir(new_report_folder)
        for file_found in files_found:
            amr_file = search("./Voicemail/[0-9]*\.amr$", file_found)
            if amr_file:
                filename = basename(file_found)
                shutil.copyfile(file_found, join(new_report_folder, filename))
            elif file_found.endswith('voicemail.db'):
                voicemail_db = str(file_found)

        db = open_sqlite_db_readonly(voicemail_db)
        cursor = db.cursor()
        cursor.execute('''
        SELECT datetime(voicemail.date, 'unixepoch') AS 'Date and time',
        voicemail.sender,
        voicemail.receiver,
		map.account AS 'ICCID receiver',
        strftime('%H:%M:%S', voicemail.duration, 'unixepoch') AS 'Duration',
        voicemail.ROWID
        FROM voicemail
		LEFT OUTER JOIN map ON voicemail.label = map.label
        WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                audio_file = join(artifact_name, f'{row[5]}.amr')
                audio_tag = f''' 
                        <audio controls src="{audio_file}" type="audio/amr" preload="none">
                            <p>Your browser does not support HTML5 audio elements.</p>
                        </audio> 
                        '''
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], audio_tag))

            report = ArtifactHtmlReport('Voicemail')
            report.start_artifact_report(report_folder, 'Voicemail')
            report.add_script()
            data_headers = ('Date and time', 'Sender', 'Receiver', 'ICCID receiver', 'Duration', 'Audio File')
            report.write_artifact_data_table(data_headers, data_list, dirname(file_found), html_no_escape=['Audio File'])
            report.end_artifact_report()

            tsvname = 'Voicemail'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Voicemail'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No voicemail found')


        cursor.execute('''
        SELECT datetime(voicemail.date, 'unixepoch') AS 'Date and time',
        voicemail.sender,
        voicemail.receiver,
		map.account AS 'ICCID receiver',
        strftime('%H:%M:%S', voicemail.duration, 'unixepoch') AS 'Duration',
        CASE voicemail.trashed_date
		WHEN 0 THEN ""
		ELSE datetime('2001-01-01', voicemail.trashed_date || ' seconds')
		END AS 'Trashed date',
        voicemail.ROWID
        FROM voicemail
		LEFT OUTER JOIN map ON voicemail.label = map.label
        WHERE voicemail.trashed_date != 0 OR voicemail.flags = 75
        ''')

        # Deleted Voicemail
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                audio_file = join(artifact_name, f'{row[6]}.amr')
                audio_tag = f''' 
                        <audio controls src="{audio_file}" type="audio/amr" preload="none">
                            <p>Your browser does not support HTML5 audio elements.</p>
                        </audio> 
                        '''
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], audio_tag))

            report = ArtifactHtmlReport('Deleted voicemail')
            report.start_artifact_report(report_folder, 'Deleted voicemail')
            report.add_script()
            data_headers = ('Date and time', 'Sender', 'Receiver', 'ICCID receiver', 'Duration', 'Trashed date', 'Audio File')
            report.write_artifact_data_table(data_headers, data_list, dirname(file_found), html_no_escape=['Audio File'])
            report.end_artifact_report()

            tsvname = 'Deleted voicemail'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Deleted voicemail'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No deleted voicemail found')

    return

__artifacts__ = {
    "voicemail": (
        "Call History",
        ('**/Voicemail/voicemail.db','**/Voicemail/*.amr'),
        get_voicemail)
}