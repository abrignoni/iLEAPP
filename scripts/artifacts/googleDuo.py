__artifacts_v2__ = {
    "googleDuoContacts": {
        "name": "Google Duo - Contacts",
        "description": "Rows of the contact table in the Google Duo or Google Meet DataStore database",
        "author": "@stark4n6", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Google Duo", "notes": "Only the first matched file whose path ends in "
                                           "DataStore is read. The path pattern is not tied to one "
                                           "app and the container is not checked. Registration Date "
                                           "and Sync Date are converted as Unix microseconds; no "
                                           "source or measurement for that unit is recorded here.",
        "paths": ('*/Application Support/DataStore*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Google Meet 225.0 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | Google Meet 257.0 | 1016 rows",
            "hickman_ios14": "iOS 14.3 | Google Duo 116.0 | 5 rows",
        }
    },
    "googleDuoCallHistory": {
        "name": "Google Duo - Call History",
        "description": "Rows of the call_history table in the Google Duo or Google Meet DataStore database, joined to the contact table for the name",
        "author": "@stark4n6", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Google Duo", "notes": "Only the first matched file whose path ends in "
                                           "DataStore is read. The path pattern is not tied to one "
                                           "app and the container is not checked. Timestamp is "
                                           "converted as Unix seconds. Call Duration is the stored "
                                           "duration read as seconds and rendered as HH:MM:SS, so a "
                                           "value of 24 hours or more wraps. Call Direction reads "
                                           "Incoming when call_history_is_outgoing_call is 0 and "
                                           "Outgoing when it is 1, and is blank for any other "
                                           "value. Video Call? reads Yes when "
                                           "call_history_is_video_call is 1. Contact Name comes "
                                           "from the contact table row whose contact_id equals "
                                           "call_history_other_user_id and is blank when there is "
                                           "none. No source for these readings is recorded here.",
        "paths": ('*/Application Support/DataStore*',),
        "output_types": "standard", "artifact_icon": "phone",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Google Meet 225.0 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | Google Meet 257.0 | 6 rows",
            "hickman_ios14": "iOS 14.3 | Google Duo 116.0 | 11 rows",
        }
    },
    "googleDuoClips": {
        "name": "Google Duo - Clips",
        "description": "Rows of the media_clip_v2 table in the Google Duo or Google Meet DataStore database, with the ClipsCache PNG named for the message id where one is found",
        "author": "@stark4n6", "creation_date": "2026-06-23", "last_update_date": "2026-07-31", "requirements": "none",
        "category": "Google Duo",
        "notes": "The media_clip_source value's direction semantics are not established; the value "
                 "is reported as stored. The Clip column shows the first matched file whose path "
                 "contains <message id>.png. Creation Date, Message Date and Viewed Date are "
                 "converted as Unix microseconds; Viewed Date is the stored media_clip_viewed_date "
                 "value and what event it marks is not established. Only the first matched file "
                 "whose path ends in DataStore is read.",
        "paths": ('*/Application Support/DataStore*', '*/Application Support/ClipsCache/*.png'),
        "output_types": "standard", "artifact_icon": "movie",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Google Meet 225.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Google Meet 257.0 | 1 row",
            "hickman_ios14": "iOS 14.3 | Google Duo 116.0 | 2 rows",
        }
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
                    ('Viewed Date', 'datetime'), 'Local User ID', 'Media Clip Source (as stored)',
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
        media_clip_source,
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
