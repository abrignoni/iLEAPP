__artifacts_v2__ = {
    'voicemail': {
        'name': 'Voicemail',
        'description': 'Extract voicemail',
        'author': '@JohannPLW - @AlexisBrignoni',
        'creation_date': '2023-09-30',
        'last_update_date': '2025-05-13',
        'requirements': "none",
        'category': 'Call History',
        'notes': '',
        'paths': (
            '*/mobile/Library/Voicemail/voicemail.db*',
            '*/mobile/Library/Voicemail/*.amr',
            '*/mobile/Library/Voicemail/*.transcript'),
        'output_types': 'standard',
        'artifact_icon': 'mic'
    }
}

import os
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, does_table_exist_in_db, get_sqlite_db_records, \
    get_plist_file_content, check_in_media, convert_unix_ts_to_utc, \
    convert_cocoa_core_data_ts_to_utc, logfunc


@artifact_processor
def voicemail(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    db_file = get_file_path(files_found, 'voicemail.db')
    data_list = []

    # Filter out voicemail files (Audio and Transcripts)
    extracted_audio_files = [
        file_path for file_path in files_found
        if str(file_path).endswith('.amr')
    ]
    extracted_transcript_files = [
        file_path for file_path in files_found
        if str(file_path).endswith('.transcript')
    ]

    if db_file:
        source_file = db_file

        table_map_exists = does_table_exist_in_db(db_file, 'map')

        if table_map_exists:
            query = '''
            SELECT
                voicemail.date,
                voicemail.sender,
                voicemail.receiver,
                map.account,
                time(voicemail.duration, 'unixepoch'),
                CASE
                    WHEN voicemail.trashed_date = 0 AND voicemail.flags = 75 THEN 'Yes'
                    WHEN voicemail.trashed_date = 0 THEN 'No'
                    ELSE voicemail.trashed_date
                END,
                voicemail.ROWID
            FROM voicemail
            LEFT OUTER JOIN map ON voicemail.label = map.label
            '''
            data_headers = (
                ('Date and time', 'datetime'), ('Sender', 'phonenumber'),
                ('Receiver', 'phonenumber'), 'ICCID receiver', 'Duration',
                'Deleted', ('Audio File', 'media'), 'Transcript',
                'Transcript confidence')
        else:
            query = '''
            SELECT
                voicemail.date,
                voicemail.sender,
                voicemail.callback_num,
                time(voicemail.duration, 'unixepoch'),
                CASE
                    WHEN voicemail.trashed_date = 0 AND voicemail.flags = 75 THEN 'Yes'
                    WHEN voicemail.trashed_date = 0 THEN 'No'
                    ELSE voicemail.trashed_date
                END,
                voicemail.ROWID
            FROM voicemail
            '''
            data_headers = (
                ('Date and time', 'datetime'), ('Sender', 'phonenumber'),
                ('Callback Number', 'phonenumber'), 'Duration', 'Deleted',
                ('Audio File', 'media'), 'Transcript', 'Transcript confidence',)

        db_records = get_sqlite_db_records(db_file, query)

        for record in db_records:
            timestamp = convert_unix_ts_to_utc(record[0])

            deleted_raw = record[-2] 
            if isinstance(deleted_raw, int) and deleted_raw != 0:
                 deleted = convert_cocoa_core_data_ts_to_utc(deleted_raw)
            else:
                 deleted = deleted_raw

            row_id = record[-1]
            audio_name_target = f'{row_id}.amr'
            transcript_name_target = f'{row_id}.transcript'

            media_item = ""
            real_audio_path = next((f for f in extracted_audio_files if str(f).endswith(audio_name_target)), None)

            if real_audio_path:
                media_item = check_in_media(real_audio_path, audio_name_target)

            transcript_file_path = get_file_path(extracted_transcript_files, transcript_name_target)
            transcript = {}
            if transcript_file_path:
                try:
                    transcript = get_plist_file_content(transcript_file_path)
                except:
                    transcript = {}

            transcription_string = transcript.get('transcriptionString', '')
            transcription_confidence = transcript.get('confidence', '')

            if table_map_exists:
                data_list.append(
                    (timestamp, record[1], record[2], record[3], record[4],
                     deleted, media_item, transcription_string,
                     transcription_confidence))
            else:
                data_list.append(
                    (timestamp, record[1], record[2], record[3], deleted,
                     media_item, transcription_string,
                     transcription_confidence))

    else:
        source_file = 'See Filename Column'
        transcriptions_map = {}
        for transcript_path in extracted_transcript_files:
            t_id = Path(transcript_path).stem
            try:
                pl = get_plist_file_content(transcript_path)
                transcriptions_map[t_id] = pl
            except:
                continue

        for audio_file_path in extracted_audio_files:
            file_name = Path(audio_file_path).name
            file_id = Path(audio_file_path).stem
            created = ''
            modified = ''
            try:
                if audio_file_path in seeker.file_infos:
                    created = convert_unix_ts_to_utc(seeker.file_infos[audio_file_path].creation_date)
                    modified = convert_unix_ts_to_utc(seeker.file_infos[audio_file_path].modification_date)
            except:
                pass

            media_item = check_in_media(audio_file_path, file_name)
            transcript_data = transcriptions_map.get(file_id, {})
            transcription_string = transcript_data.get('transcriptionString', '')
            confidence = transcript_data.get('confidence', '')

            data_list.append((
                created,
                modified,
                file_name,
                media_item,
                transcription_string,
                confidence
            ))

        data_headers = (
            ('File Created', 'datetime'), ('File Modified', 'datetime'),
            'Audio Filename', ('Audio File', 'media'),
            'Transcript', 'Transcript confidence')

    return data_headers, data_list, source_file
