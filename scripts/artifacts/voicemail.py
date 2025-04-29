__artifacts_v2__ = {
    'voicemail': {
        'name': 'Voicemail',
        'description': 'Extract voicemail',
        'author': '@JohannPLW - @AlexisBrignoni',
        'creation_date': '2023-09-30',
        'last_update_date': '2025-04-15',
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


import inspect
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, does_table_exist_in_db, get_sqlite_db_records, get_plist_file_content, \
    check_in_media, convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc


@artifact_processor
def voicemail(files_found, report_folder, seeker, wrap_text, timezone_offset):
    artifact_info = inspect.stack()[0]
    db_file = get_file_path(files_found, 'voicemail.db')
    data_list = []

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
        ('Callback Number', 'phonenumber'), 'Duration', 'Deleted', ('Audio File', 'media'), 
        'Transcript', 'Transcript confidence',)

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
            ('Date and time', 'datetime'), ('Sender', 'phonenumber'), ('Receiver', 'phonenumber'), 
            'ICCID receiver', 'Duration', 'Deleted', ('Audio File', 'media'), 'Transcript', 
            'Transcript confidence')

    db_records = get_sqlite_db_records(db_file, query)
    
    # Filter out voicemail files which are stored in a sub-folder
    extracted_audio_files = [
        file_path for file_path in files_found \
            if Path(file_path).parent.name == 'Voicemail' and Path(file_path).suffix == '.amr']
    extracted_transcript_files = [
        file_path for file_path in files_found \
            if Path(file_path).parent.name == 'Voicemail' and Path(file_path).suffix == '.transcript']

    if db_file:
        source_file = db_file

        for record in db_records:
            timestamp = convert_unix_ts_to_utc(record[0])
            deleted = convert_cocoa_core_data_ts_to_utc(record[-2]) \
                if isinstance(record[-2], int) else record[-2]
            audio_filename = f'{record[-1]}.amr'
            media_item = check_in_media(seeker, audio_filename, artifact_info, \
                                        name=audio_filename, already_extracted=extracted_audio_files)
            transcript_file_path = get_file_path(extracted_transcript_files, f'{record[-1]}.transcript')
            transcript = get_plist_file_content(transcript_file_path) if transcript_file_path else {}
            transcription_string = transcript.get('transcriptionString', '')
            transcription_confidence = transcript.get('confidence', '')
            if table_map_exists:
                data_list.append(
                    (timestamp, record[1], record[2], record[3], record[4], deleted, media_item, 
                    transcription_string, transcription_confidence))
            else:
                data_list.append(
                    (timestamp, record[1], record[2], record[3], deleted, media_item, 
                    transcription_string, transcription_confidence))
    else:
        source_file = 'See Filename Column'
        transcriptions = {}

        for transcript_file_path in extracted_transcript_files:
            transcript_key = Path(transcript_file_path).stem
            transcript = get_plist_file_content(transcript_file_path)
            transcriptions[transcript_key] = {
                'path': seeker.file_infos[transcript_file_path].source_path,
                'transcription_string': transcript.get('transcriptionString', ''),
                'confidence': transcript.get('confidence', '')
            }

        for audio_file_path in extracted_audio_files:
            audio_key = Path(audio_file_path).stem
            data_list.append((
                convert_unix_ts_to_utc(seeker.file_infos[audio_file_path].creation_date),
                convert_unix_ts_to_utc(seeker.file_infos[audio_file_path].modification_date),
                seeker.file_infos[audio_file_path].source_path,
                check_in_media(seeker, audio_file_path, artifact_info, \
                    name=Path(audio_file_path).name, already_extracted=extracted_audio_files),
                transcriptions.get(audio_key, {}).get('path', ''),
                transcriptions.get(audio_key, {}).get('transcription_string', ''),
                transcriptions.get(audio_key, {}).get('confidence', '')
                ))

        data_headers = (
            ('File Created', 'datetime'), ('File Modified', 'datetime'), 
            'Audio Filename', ('Audio File', 'media'), 'Transcript Filename', 
            'Transcript', 'Transcript confidence')

    return data_headers, data_list, source_file
