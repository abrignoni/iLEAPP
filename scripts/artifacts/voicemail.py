__artifacts_v2__ = {
    "voicemail": {
        "name": "Voicemail",
        "description": "Parses and extract Voicemail",
        "author": "@JohannPLW - @AlexisBrignoni",
        "version": "0.0.4",
        "date": "2023-10-29",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('**/Voicemail/voicemail.db','**/Voicemail/*.amr'),
        "function": "get_voicemail"
    }
}

from os.path import basename, dirname
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, media_to_html, does_table_exist, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_voicemail(files_found, report_folder, seeker, wrap_text, timezone_offset):

    files_found = [file for file in files_found 
                   if basename(dirname(file)) == "Voicemail"]

    for file_found in files_found:
        if file_found.endswith('voicemail.db'):
            voicemail_db = str(file_found)

            db = open_sqlite_db_readonly(voicemail_db)
            cursor = db.cursor()

            table_map_exists = does_table_exist(db, 'map')

            if table_map_exists:
                db_query = '''
                    SELECT datetime(voicemail.date, 'unixepoch') AS 'Date and time',
                    voicemail.sender,
                    voicemail.receiver,
                    map.account AS 'ICCID receiver',
                    strftime('%H:%M:%S', voicemail.duration, 'unixepoch') AS 'Duration',
                    voicemail.ROWID
                    FROM voicemail
                    LEFT OUTER JOIN map ON voicemail.label = map.label
                    WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
                '''
                data_headers = ('Date and time', 'Sender', 'Receiver', 'ICCID receiver', 'Duration', 'Audio File')
            else:
                db_query = '''
                    SELECT datetime(voicemail.date, 'unixepoch') AS 'Date and time',
                    voicemail.sender,
                    voicemail.callback_num,
                    strftime('%H:%M:%S', voicemail.duration, 'unixepoch') AS 'Duration',
                    voicemail.ROWID
                    FROM voicemail
                    WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
                '''
                data_headers = ('Date and time', 'Sender', 'Callback Number', 'Duration', 'Audio File')

            cursor.execute(db_query)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    timestamp = convert_ts_human_to_utc(row[0])
                    timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)        
                    audio_file = f'{row[-1]}.amr'
                    audio_tag = media_to_html(audio_file, files_found, report_folder)
                    if table_map_exists:
                        data_list.append(
                            (timestamp, row[1], row[2], row[3], row[4], audio_tag))
                    else:
                        data_list.append(
                            (timestamp, row[1], row[2], row[3], audio_tag))

                report = ArtifactHtmlReport('Voicemail')
                report.start_artifact_report(report_folder, 'Voicemail')
                report.add_script()
                report.write_artifact_data_table(data_headers, data_list, dirname(file_found), html_no_escape=['Audio File'])
                report.end_artifact_report()

                tsvname = 'Voicemail'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Voicemail'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No voicemail found')


            # Deleted Voicemail

            if table_map_exists:
                db_query = '''
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
                '''
                data_headers = ('Date and time', 'Sender', 'Receiver', 'ICCID receiver', 'Duration', 'Trashed date', 'Audio File')
            else:
                db_query = '''
                    SELECT datetime(voicemail.date, 'unixepoch') AS 'Date and time',
                    voicemail.sender,
                    voicemail.callback_num,
                    strftime('%H:%M:%S', voicemail.duration, 'unixepoch') AS 'Duration',
                    CASE voicemail.trashed_date
                    WHEN 0 THEN ""
                    ELSE datetime('2001-01-01', voicemail.trashed_date || ' seconds')
                    END AS 'Trashed date',
                    voicemail.ROWID
                    FROM voicemail
                    WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
                '''
                data_headers = ('Date and time', 'Sender', 'Callback Number', 'Duration', 'Trashed date', 'Audio File')

            cursor.execute(db_query)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    timestamp = convert_ts_human_to_utc(row[0])
                    timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)        
                    audio_file = f'{row[-1]}.amr'
                    audio_tag = media_to_html(audio_file, files_found, report_folder)
                    if table_map_exists:
                        data_list.append(
                            (timestamp, row[1], row[2], row[3], row[4], row[5], audio_tag))
                    else:
                        data_list.append(
                            (timestamp, row[1], row[2], row[3], row[4], audio_tag))

                report = ArtifactHtmlReport('Deleted voicemail')
                report.start_artifact_report(report_folder, 'Deleted voicemail')
                report.add_script()
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