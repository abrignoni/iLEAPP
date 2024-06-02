__artifacts_v2__ = {
    "googleTranslate": {
        "name": "Google Translate",
        "description": "History, Favorite translations and Text-To-Speech",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "version": "0.1.0",
        "date": "30/05/2024",
        "requirements": "none",
        "category": "Google Translate",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/translate.db*'),
        "function": "get_google_translate"
    }
}

import os
import sys
import shutil
import sqlite3
import textwrap
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_table_exist, convert_utc_human_to_timezone, convert_ts_human_to_utc
from scripts.filetype import audio_match


# history
def get_history(file_found, report_folder, database, timezone_offset):
    try:
        cursor = database.cursor()
        cursor.execute('''
        SELECT
            ROWID AS "_id",
            datetime (timestamp, 'unixepoch') AS "timestamp",
            (sourcelanguage || '->' || targetlanguage) AS "fromToLang",
            sourcetext,
            targettext,
            star,
            romanization
        FROM history
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Translate History')
            report.start_artifact_report(report_folder, 'Google Translate History')
            report.add_script()
            data_headers = ('Created', 'Language', 'Source text', 'Target text', 'Starred', 'Romanization', 'Location') 
            data_list = []

            for row in all_rows:
                # timestamp
                timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]), timezone_offset)

                # starred
                starred = row[5] == 1

                # location
                location = f'history (ROWID: {row[0]})'

                # row
                data_list.append((timestamp, row[2], row[3], row[4], starred, row[6], location))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
                
            tsvname = f'Google Translate History'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Google Translate History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Translate History data available')

    except Exception as ex:
        logfunc('Exception while parsing Google Translate History: ' + str(ex))


# starred
def get_starred(file_found, report_folder, database, timezone_offset):
    try:
        cursor = database.cursor()
        cursor.execute('''
        SELECT
            ROWID AS "_id",
            (sourcelanguage || '->' || targetlanguage) AS "fromToLang",
            sourcetext,
            targettext,
            romanization
        FROM starred
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Translate Favorite Translations')
            report.start_artifact_report(report_folder, 'Google Translate Favorite Translations')
            report.add_script()
            data_headers = ('Language', 'Source text', 'Target text', 'Romanization', 'Location') 
            data_list = []

            for row in all_rows:
                # location
                location = f'starred (ROWID: {row[0]})'

                # row
                data_list.append((row[1], row[2], row[3], row[4], location))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
                
            tsvname = f'Google Translate Favorite Translations'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Google Translate Favorite Translations'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Translate Favorite Translations data available')

    except Exception as ex:
        logfunc('Exception while parsing Google Translate Favorite Translations: ' + str(ex))


# tts
def get_tts(file_found, report_folder, database, timezone_offset):
    try:
        if not does_table_exist(database, 'tts'):
            return

        cursor = database.cursor()
        cursor.execute('''
        SELECT
            ROWID AS "_id",
            language,
            text,
            audio
        FROM tts
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Translate Text-To-Speech')
            report.start_artifact_report(report_folder, 'Google Translate Text-To-Speech')
            report.add_script()
            data_headers = ('Language', 'Text', 'Audio', 'Location') 
            data_list = []

            for row in all_rows:
                audio_html = ''
                # audio
                audio = row[3]
                if bool(audio):
                    mimetype = audio_match(audio)
                    if bool(mimetype):
                        Path(f'{report_folder}').mkdir(parents=True, exist_ok=True)
                        audio_filename = f'audio_{row[0]}.{mimetype.extension}'
                        audio_path = os.path.join(report_folder, audio_filename)
                        with open(audio_path, "wb") as audio_file:
                            audio_file.write(audio)
                        audio_path_html = Path(report_folder).name + '/' + audio_filename                       
                        audio_html = f'<audio controls><source src="{audio_path_html}" type="audio/ogg"><source src="{audio_path_html}" type="audio/mpeg">Your browser does not support the audio element.</audio>'

                # location
                location = f'tts (ROWID: {row[0]})'

                # row
                data_list.append((row[1], row[2], audio_html, location))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Audio'])
            report.end_artifact_report()
                
            tsvname = f'Google Translate Text-To-Speech'
            tsv(report_folder, data_headers, data_list, tsvname)
                
            tlactivity = 'Google Translate Text-To-Speech'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Translate Text-To-Speech data available')

    except Exception as ex:
        logfunc('Exception while parsing Google Translate Text-To-Speech: ' + str(ex))


# google translate
def get_google_translate(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        files_found = str(file_found)
        
        # translate.db
        if file_found.endswith('translate.db'):
            db = open_sqlite_db_readonly(files_found)
            try:
                # history
                get_history(file_found, report_folder, db, timezone_offset)

                # favorite translations
                get_starred(file_found, report_folder, db, timezone_offset)

                # text-to-speech
                get_tts(file_found, report_folder, db, timezone_offset)

            finally:
                db.close()
