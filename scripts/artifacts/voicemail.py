__artifacts_v2__ = {
    "voicemail": {
        "name": "Voicemail",
        "description": "Extract voicemail",
        "author": "@JohannPLW - @AlexisBrignoni",
        "version": "0.1.1",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/mobile/Library/Voicemail/voicemail.db*',),
        "output_types": "standard",
        "artifact_icon": "mic"
    },
    "deletedVoicemail": {
        "name": "Deleted Voicemail",
        "description": "Extract deleted voicemail",
        "author": "@JohannPLW - @AlexisBrignoni",
        "version": "0.1.1",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/mobile/Library/Voicemail/voicemail.db*',),
        "output_types": "standard",
        "artifact_icon": "mic-off"
    }
}

import inspect
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, does_table_exist, get_sqlite_db_records, check_in_media, \
    convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def voicemail(files_found, report_folder, seeker, wrap_text, timezone_offset):
    artifact_info = inspect.stack()[0]
    db_file = get_file_path(files_found, "voicemail.db")
    data_list = []

    query = '''
    SELECT 
        voicemail.date,
        voicemail.sender,
        voicemail.receiver,
        map.account,
        strftime('%H:%M:%S', voicemail.duration, 'unixepoch'),
        voicemail.ROWID
    FROM voicemail
    LEFT OUTER JOIN map ON voicemail.label = map.label
    WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
    '''
    
    data_headers = (
        ('Date and time', 'datetime'), ('Sender', 'phonenumber'), ('Receiver', 'phonenumber'), 
        'ICCID receiver', 'Duration', ('Audio File', 'media'))
    
    table_map_exists = does_table_exist(db_file, 'map')

    if not table_map_exists:
        query = '''
        SELECT 
            voicemail.date,
            voicemail.sender,
            voicemail.callback_num,
            strftime('%H:%M:%S', voicemail.duration, 'unixepoch'),
            voicemail.ROWID
        FROM voicemail
        WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
        '''

        data_headers = (
            ('Date and time', 'datetime'), ('Sender', 'phonenumber'), ('Callback Number', 'phonenumber'), 
            'Duration', ('Audio File', 'media'))

    db_records = get_sqlite_db_records(db_file, query)
    
    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[0])
        audio_filename = f'{record[-1]}.amr'
        audio_file_path = f'*/mobile/Library/Voicemail/{audio_filename}'
        media_item = check_in_media(seeker, audio_file_path, artifact_info)
        if table_map_exists:
            data_list.append(
                (timestamp, record[1], record[2], record[3], record[4], media_item.id))
        else:
            data_list.append(
                (timestamp, record[1], record[2], record[3], media_item.id))
    return data_headers, data_list, db_file

@artifact_processor
def deletedVoicemail(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_file = get_file_path(files_found, "voicemail.db")
    data_list = []
    artifact_info = inspect.stack()[0]

    query = '''
    SELECT 
        voicemail.date,
        voicemail.sender,
        voicemail.receiver,
        map.account,
        strftime('%H:%M:%S', voicemail.duration, 'unixepoch'),
        CASE voicemail.trashed_date
        WHEN 0 THEN ""
        ELSE voicemail.trashed_date
        END,
        voicemail.ROWID
    FROM voicemail
    LEFT OUTER JOIN map ON voicemail.label = map.label
    WHERE voicemail.trashed_date != 0 OR voicemail.flags = 75
    '''

    data_headers = (
        ('Date and time', 'datetime'), ('Sender', 'phonenumber'), ('Receiver', 'phonenumber'), 
        'ICCID receiver', 'Duration', ('Trashed date', 'datetime'), ('Audio File', 'media'))

    table_map_exists = does_table_exist(db_file, 'map')

    if not table_map_exists:
        query = '''
        SELECT 
            voicemail.date,
            voicemail.sender,
            voicemail.callback_num,
            strftime('%H:%M:%S', voicemail.duration, 'unixepoch'),
            CASE voicemail.trashed_date
            WHEN 0 THEN ""
            ELSE voicemail.trashed_date
            END,
        voicemail.ROWID
        FROM voicemail
        WHERE voicemail.trashed_date = 0 AND voicemail.flags != 75
        '''

        data_headers = (
        ('Date and time', 'datetime'), ('Sender', 'phonenumber'), ('Callback Number', 'phonenumber'), 
        'Duration', ('Trashed date', 'datetime'), ('Audio File', 'media'))

    db_records = get_sqlite_db_records(db_file, query)

    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[0])
        trashed_date = convert_cocoa_core_data_ts_to_utc(record[-2])
        audio_filename = f'{record[-1]}.amr'
        audio_file_path = f'*/mobile/Library/Voicemail/{audio_filename}'
        media_item = check_in_media(seeker, audio_file_path, artifact_info)
        if table_map_exists:
            data_list.append(
                (timestamp, record[1], record[2], record[3], record[4], trashed_date, media_item.id))
        else:
            data_list.append(
                (timestamp, record[1], record[2], record[3], trashed_date, media_item.id))

    return data_headers, data_list, db_file
