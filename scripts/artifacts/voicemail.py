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
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, media_to_html


def get_voicemail(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        if file_found.endswith('voicemail.db'):
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
                audio_file = f'{row[5]}.amr'
                audio_tag = media_to_html(audio_file, files_found, report_folder)
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
                audio_file = f'{row[6]}.amr'
                audio_tag = media_to_html(audio_file, files_found, report_folder)
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