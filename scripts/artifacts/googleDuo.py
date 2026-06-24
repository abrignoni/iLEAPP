__artifacts_v2__ = {
    "googleDuoContacts": {
        "name": "Google Duo - Contacts",
        "description": "Google Duo contacts",
        "author": "", "version": "2.0", "date": "2026-06-23", "requirements": "none",
        "category": "Google Duo", "notes": "",
        "paths": ('*/Application Support/DataStore*',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "googleDuoCallHistory": {
        "name": "Google Duo - Call History",
        "description": "Google Duo call history",
        "author": "", "version": "2.0", "date": "2026-06-23", "requirements": "none",
        "category": "Google Duo", "notes": "",
        "paths": ('*/Application Support/DataStore*',),
        "output_types": "standard", "artifact_icon": "phone"
    },
    "googleDuoClips": {
        "name": "Google Duo - Clips",
        "description": "Google Duo media clips (with thumbnails from ClipsCache)",
        "author": "", "version": "2.0", "date": "2026-06-23", "requirements": "none",
        "category": "Google Duo", "notes": "",
        "paths": ('*/Application Support/DataStore*', '*/Application Support/ClipsCache/*.png'),
        "output_types": "standard", "artifact_icon": "film"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, check_in_media


def _find_datastore(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('DataStore'):
            return file_found
    return ''


@artifact_processor
def googleDuoContacts(context):
    data_headers = (('Registration Date', 'datetime'), 'Name', 'ID', 'Number Label',
                    ('Sync Date', 'datetime'))
    data_list = []
    db_path = _find_datastore(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(contact_reg_data_timestamp/1000000, 'unixepoch'),
        contact_name,
        contact_id,
        contact_number_label,
        datetime(contact_sync_date/1000000, 'unixepoch')
    FROM contact
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def googleDuoCallHistory(context):
    data_headers = (('Timestamp', 'datetime'), 'Local User ID', 'Remote User ID', 'Contact Name',
                    'Call Duration', 'Call Direction', 'Video Call?')
    data_list = []
    db_path = _find_datastore(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(call_history.call_history_timestamp, 'unixepoch'),
        call_history.call_history_local_user_id,
        call_history.call_history_other_user_id,
        contact.contact_name,
        strftime('%H:%M:%S', call_history.call_history_duration, 'unixepoch'),
        CASE call_history.call_history_is_outgoing_call WHEN 0 THEN 'Incoming' WHEN 1 THEN 'Outgoing' END,
        CASE call_history.call_history_is_video_call WHEN 0 THEN '' WHEN 1 THEN 'Yes' END
    FROM call_history
    LEFT JOIN contact ON call_history.call_history_other_user_id = contact.contact_id
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def googleDuoClips(context):
    data_headers = (('Creation Date', 'datetime'), ('Message Date', 'datetime'),
                    ('Viewed Date', 'datetime'), 'Local User ID', 'Clip Direction',
                    'Text Representation', 'Message ID', 'MD5 Checksum', 'Content Size',
                    'Transferred Size', ('Clip', 'media'))
    data_list = []
    db_path = _find_datastore(context)
    if not db_path:
        return data_headers, data_list, ''
    files = [str(f) for f in context.get_files_found()]

    query = '''
    SELECT
        datetime(media_clip_creation_date/1000000, 'unixepoch'),
        datetime(media_clip_message_date/1000000, 'unixepoch'),
        datetime(media_clip_viewed_date/1000000, 'unixepoch'),
        media_clip_local_id,
        CASE media_clip_source WHEN 0 THEN 'Received' WHEN 1 THEN 'Sent' END,
        media_clip_text_representation,
        media_clip_message_id,
        media_clip_md5_checksum,
        media_clip_content_size,
        media_clip_transferred_size
    FROM media_clip_v2
    '''
    for row in get_sqlite_db_records(db_path, query):
        clip_name = f'{row[6]}.png'
        media_ref = ''
        for match in files:
            if clip_name in match:
                media_ref = check_in_media(match)
                break
        data_list.append((*tuple(row), media_ref))
    return data_headers, data_list, context.get_relative_path(db_path)
