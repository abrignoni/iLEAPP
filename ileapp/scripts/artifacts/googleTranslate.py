__artifacts_v2__ = {
    "googleTranslateHistory": {
        "name": "Google Translate History",
        "description": "History from Google Translate App",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-01-09",
        "requirements": "none",
        "category": "Translator",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/translate.db*'),
        "output_types": "standard",
        "artifact_icon": "type"
    },
    "googleTranslateStarred": {
        "name": "Google Translate Favorite Translations",
        "description": "Favorite translations from Google Translate App",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-01-09",
        "requirements": "none",
        "category": "Translator",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/translate.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star"
    },
    "googleTranslateTts": {
        "name": "Google Translate Text-To-Speech",
        "description": "Text-To-Speech from Google Translate App",
        "author": "Django Faiola (djangofaiola.blogspot.com)",
        "creation_date": "2024-05-30",
        "last_update_date": "2025-01-09",
        "requirements": "none",
        "category": "Translator",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/translate.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "volume-2",
        "html_columns": ['Audio']
    }
}

import os
from pathlib import Path
from ileapp.scripts.filetype import audio_match
from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, does_table_exist_in_db, convert_unix_ts_to_utc

@artifact_processor
def googleTranslateHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "translate.db")
    data_list = []

    query = '''
    SELECT
        ROWID AS "_id",
        timestamp AS "timestamp",
        (sourcelanguage || '->' || targetlanguage) AS "fromToLang",
        sourcetext,
        targettext,
        star,
        romanization
    FROM history
    '''

    data_headers = (
        ('Created', 'datetime'), 
        'Language', 
        'Source text', 
        'Target text', 
        'Starred', 
        'Romanization', 
        'Location') 

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[1])  # timestamp
        starred = record[5] == 1  # starred
        location = f'history (ROWID: {record[0]})'  # location

        data_list.append((timestamp, record[2], record[3], record[4], starred, record[6], location))
    
    return data_headers, data_list, source_path


@artifact_processor
def googleTranslateStarred(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "translate.db")
    data_list = []

    query = '''
    SELECT
        ROWID AS "_id",
        (sourcelanguage || '->' || targetlanguage) AS "fromToLang",
        sourcetext,
        targettext,
        romanization
    FROM starred
    '''

    data_headers = ('Language', 'Source text', 'Target text', 'Romanization', 'Location')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        location = f'starred (ROWID: {record[0]})'  # location

        data_list.append((record[1], record[2], record[3], record[4], location))

    return data_headers, data_list, source_path


@artifact_processor
def googleTranslateTts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "translate.db")
    data_list = []
    data_list_html = []

    if not does_table_exist_in_db(source_path, 'tts'):
        return (), data_list, source_path

    query = '''
    SELECT
        ROWID AS "_id",
        language,
        text,
        audio
    FROM tts
    '''

    data_headers = ('Language', 'Text', 'Audio', 'Location') 

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        # audio
        audio_html = ''
        audio = record[3]
        if bool(audio):
            mimetype = audio_match(audio)
            if bool(mimetype):
                Path(f'{report_folder}').mkdir(parents=True, exist_ok=True)
                audio_filename = f'audio_{record[0]}.{mimetype.extension}'
                audio_path = os.path.join(report_folder, audio_filename)
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(audio)
                audio_path_html = Path(report_folder).name + '/' + audio_filename                       
                audio_html = f'<audio controls><source src="{audio_path_html}" type="audio/ogg"><source src="{audio_path_html}" type="audio/mpeg">Your browser does not support the audio element.</audio>'

        location = f'tts (ROWID: {record[0]})'  # location

        data_list.append((record[1], record[2], audio_path, location))
        data_list_html.append((record[1], record[2], audio_html, location))

    return data_headers, (data_list, data_list_html), source_path
