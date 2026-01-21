""" See descriptions below """

__artifacts_v2__ = {
    "get_viber_settings": {
        "name": "Viber - Settings",
        "description": "Parses Viber user settings and configuration.",
        "author": "@theAtropos4n6",
        "creation_date": "2022-03-08",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": ('*/com.viber/settings/Settings.data*',),
        "output_types": "standard",
        "artifact_icon": "settings"
    },
    "get_viber_contacts": {
        "name": "Viber - Contacts",
        "description": "Parses Viber contacts list.",
        "author": "@theAtropos4n6",
        "creation_date": "2022-03-08",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": ('*/com.viber/database/Contacts.data*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "get_viber_call_remnants": {
        "name": "Viber - Call Remnants",
        "description": "Parses recent calls with no corresponding message entry (deleted messages indicator).",
        "author": "@theAtropos4n6",
        "creation_date": "2022-03-08",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": ('*/com.viber/database/Contacts.data*', '*/com.viber/settings/Settings.data*'),
        "output_types": "standard",
        "artifact_icon": "phone-missed"
    },
    "get_viber_chats": {
        "name": "Viber - Chats",
        "description": "Parses Viber chats, messages, attachments and location data.",
        "author": "@theAtropos4n6",
        "creation_date": "2022-03-08",
        "last_update_date": "2025-11-28",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": (
            '*/com.viber/database/Contacts.data*',
            '*/com.viber/settings/Settings.data*',
            '*/Containers/Data/Application/*/Documents/Attachments/*.*',
            '*/com.viber/ViberIcons/*.*'
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }

}
}

import json
import os
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    get_file_path,
    get_sqlite_db_records,
    convert_cocoa_core_data_ts_to_utc,
    check_in_media
)

def get_viber_user_settings(files_found):
    settings = {'_myUserName': '', '_myPhoneNumber': ''}
    source_path = get_file_path(files_found, 'Settings.data')

    if source_path:
        query = '''
        SELECT Data.key, value
        FROM Data
        WHERE Data.key IN ('_myUserName', '_myPhoneNumber')
        '''
        rows = get_sqlite_db_records(source_path, query)
        for row in rows:
            settings[row[0]] = row[1]
    return settings


@artifact_processor
def get_viber_settings(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Settings.data')
    data_list = []

    if not source_path:
        logfunc('Viber Settings.data not found')
        return (), [], ''

    query = '''
        SELECT Data.key, value
        FROM Data
        WHERE Data.key IN (
            '_myUserName', '_currentEmail', '_myPhoneNumber', '_myCanonizedPhoneNumber',
            '_myFormattedPhoneNumber', '_myCountryPhoneCode', '_myCountryCode',
            '_myLanguageCode', '_wasabiLastKnownUserLocation', '_uid', '_appVersion',
            '_savedDeviceId', '_attemptsToDownloadBackupForRestore', '_backupAttemptsCount',
            '_hiddenChatsPINData', '_myPhotoLocalID'
        )
        UNION
        SELECT Data.key, value -- Timestamps will be handled in Python
        FROM Data
        WHERE Data.key IN ('_registrationDate', '_autoBackupLastRunTime', '_lastBackupStartDate')
        UNION
        SELECT Data.key, value
        FROM Data
        WHERE Data.key IS '_birthdate'
        ORDER BY value
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        key = row[0]
        value = row[1]

        if key == '_appVersion': key = 'Application Version'
        elif key == '_lastBackupStartDate':
            key = 'Last Backup Start Date'
            if not str(value).startswith("-"):
                value = convert_cocoa_core_data_ts_to_utc(value)
        elif key == '_myUserName': key = 'User Name'
        elif key == '_currentEmail': key = 'Current Email'
        elif key == '_birthdate':
            key = 'Birth Date'
            value = convert_cocoa_core_data_ts_to_utc(value)
        elif key == '_registrationDate':
            key = 'Registration Date'
            if not str(value).startswith("-"):
                 value = convert_cocoa_core_data_ts_to_utc(value)
        elif key == '_autoBackupLastRunTime':
            key = 'Auto Backup Last Run Time'
            if not str(value).startswith("-"):
                 value = convert_cocoa_core_data_ts_to_utc(value)
        elif key == '_uid': key = 'User ID'
        elif key == '_myPhoneNumber': key = 'Phone Number'
        elif key == '_myCanonizedPhoneNumber': key = 'Canonized Phone Number'
        elif key == '_myFormattedPhoneNumber': key = 'Formatted Phone Number'
        elif key == '_myCountryPhoneCode': key = 'Country Phone Code'
        elif key == '_myCountryCode': key = 'Country Code'
        elif key == '_myLanguageCode': key = 'Language Code'
        elif key == '_wasabiLastKnownUserLocation': key = 'Last Known User Location'
        elif key == '_savedDeviceId': key = 'Device ID'
        elif key == '_myPhotoLocalID': key = 'Profile Picture ID'
        elif key == '_attemptsToDownloadBackupForRestore': key = 'Attempts To Download Backup For Restore'
        elif key == '_backupAttemptsCount': key = 'Backup Attempts Count'
        elif key == '_hiddenChatsPINData': key = 'Hidden Chats PIN Data'

        data_list.append((key, str(value)))

    data_headers = ('Setting', 'Value')
    return data_headers, data_list, source_path


@artifact_processor
def get_viber_contacts(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Contacts.data')
    data_list = []

    if not source_path:
        logfunc('Viber Contacts.data not found')
        return (), [], ''

    query = '''
        SELECT
            ZABCONTACT.ZMAINNAME AS 'Main Name',
            ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
            ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
            ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
            ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
            ZABCONTACT.ZCONTACTID AS 'Contact ID'
        FROM ZABCONTACT
        LEFT JOIN ZABCONTACTNUMBER ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
        UNION
        SELECT
            ZABCONTACT.ZMAINNAME AS 'Main Name',
            ZABCONTACT.ZPREFIXNAME AS 'Prefix Name',
            ZABCONTACT.ZSUFFIXNAME AS 'Suffix Name',
            ZABCONTACTNUMBER.ZPHONE AS 'Phone Number',
            ZABCONTACTNUMBER.ZCANONIZEDPHONENUM AS 'Canonized Phone Number',
            ZABCONTACT.ZCONTACTID AS 'Contact ID'
        FROM ZABCONTACTNUMBER
        LEFT JOIN ZABCONTACT ON ZABCONTACT.Z_PK = ZABCONTACTNUMBER.ZCONTACT
        ORDER BY ZMAINNAME
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

    data_headers = (
        'Main Name',
        'Prefix Name',
        'Suffix Name',
        'Phone Number',
        'Canonized Phone Number',
        'Contact ID'
        )
    return data_headers, data_list, source_path


@artifact_processor
def get_viber_call_remnants(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Contacts.data')
    data_list = []

    if not source_path:
        logfunc('Viber Contacts.data not found')
        return (), [], ''

    user_settings = get_viber_user_settings(files_found)

    query = '''
        SELECT
            ZRECENT.ZDATE,
            ZRECENTSLINE.ZPHONENUMBER AS 'PHONE NUMBER',
            CASE
                WHEN ZRECENT.ZCALLTYPE = 'missed' THEN 'Missed Audio Call'
                WHEN ZRECENT.ZCALLTYPE = 'missed_with_video' THEN 'Missed Video Call'
                WHEN ZRECENT.ZCALLTYPE = 'outgoing_viber' THEN 'Outgoing Audio Call'
                WHEN ZRECENT.ZCALLTYPE = 'outgoing_viber_with_video' THEN 'Outgoing Video Call'
                WHEN ZRECENT.ZCALLTYPE = 'incoming_with_video' THEN 'Incoming Video Call'
                WHEN ZRECENT.ZCALLTYPE = 'incoming' THEN 'Incoming Audio Call'
                ELSE ZRECENT.ZCALLTYPE
            end AS 'Call Type',
            ZRECENT.ZDURATION AS 'Duration'
        FROM ZRECENT
        LEFT JOIN ZRECENTSLINE ON ZRECENT.ZRECENTSLINE = ZRECENTSLINE.Z_PK
        WHERE ZRECENT.ZCALLLOGMESSAGE IS NULL AND ZRECENT.ZRECENTSLINE IS NULL
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(row[0])
        caller = row[1]
        call_type = row[2]
        duration = row[3]

        if 'Outgoing' in str(call_type) and user_settings.get('_myUserName'):
            caller = f"{user_settings['_myUserName']}, {user_settings.get('_myPhoneNumber','')}"

        data_list.append((timestamp, caller, call_type, duration))

    data_headers = (('Timestamp', 'datetime'), 'Caller', 'Call Type', 'Duration')
    return data_headers, data_list, source_path


@artifact_processor
def get_viber_chats(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Contacts.data')
    data_list = []

    if not source_path:
        logfunc('Viber Contacts.data not found')
        return (), [], ''

    user_settings = get_viber_user_settings(files_found)
    
    attachment_files = {os.path.basename(str(f)): str(f) for f in files_found if 'Attachments' in str(f) or 'ViberIcons' in str(f)}

    query = '''
        SELECT 
            CHAT_MEMBER.ZDISPLAYFULLNAME,
            CHAT_MEMBER.ZDISPLAYSHORTNAME,
            CHAT_MEMBER.ZPHONE,
            CHATS.Chat_Name,
            CHATS.CHAT_MEMBERS,
            CHATS.CHAT_PHONES,
            ZVIBERMESSAGE.ZSTATEDATE,  -- Message Creation Date
            ZVIBERMESSAGE.ZDATE,       -- Message Change State Date
            RECENT.ZDATE,              
           CASE
                WHEN RECENT.ZCALLTYPE = 'missed' THEN 'Missed Audio Call'
                WHEN RECENT.ZCALLTYPE = 'missed_with_video' THEN 'Missed Video Call'
                WHEN RECENT.ZCALLTYPE = 'outgoing_viber' THEN 'Outgoing Audio Call'
                WHEN RECENT.ZCALLTYPE = 'outgoing_viber_with_video' THEN 'Outgoing Video Call'
                WHEN RECENT.ZCALLTYPE = 'incoming_with_video' THEN 'Incoming Video Call'
                WHEN RECENT.ZCALLTYPE = 'incoming' THEN 'Incoming Audio Call'
                ELSE RECENT.ZCALLTYPE
            end AS 'Call Type',
            CASE
                WHEN ZVIBERMESSAGE.ZSTATE IN ('send','delivered') THEN 'Outgoing'
                WHEN ZVIBERMESSAGE.ZSTATE = 'received' THEN 'Incoming'
                ELSE ZVIBERMESSAGE.ZSTATE
            END AS 'State',
            RECENT.ZDURATION,
            ZVIBERMESSAGE.ZSYSTEMTYPE,
            ZVIBERMESSAGE.ZMETADATA,
            ZVIBERMESSAGE.ZTEXT,
            ZATTACHMENT.ZNAME,
            ZATTACHMENT.ZTYPE,
            ZATTACHMENT.ZFILESIZE,
            ZVIBERLOCATION.ZLATITUDE,
            ZVIBERLOCATION.ZLONGITUDE,
            CHATS.Chat_Deleted,
            ZVIBERMESSAGE.ZBEINGDELETED,
            CHATS.ZTIMEBOMBDURATION,
            ZVIBERMESSAGE.ZTIMEBOMBDURATION,
            ZVIBERMESSAGE.ZTIMEBOMBTIMESTAMP,
            CHATS.Chat_Favorite,
            ZVIBERMESSAGE.ZLIKESCOUNT
        FROM ZVIBERMESSAGE
        LEFT JOIN
            (SELECT
                ZVIBERMESSAGE.ZCONVERSATION,
                ZCONVERSATION.ZNAME AS 'Chat_Name',
                ZCONVERSATION.ZBEINGDELETED AS 'Chat_Deleted',
                ZCONVERSATION.ZFAVORITE AS 'Chat_Favorite',
                ZCONVERSATION.ZTIMEBOMBDURATION,
                coalesce(ZVIBERMESSAGE.ZPHONENUMINDEX,ZCONVERSATION.ZINTERLOCUTOR) AS 'MEMBER_ID',
                MEMBER.ZDISPLAYFULLNAME,
                group_concat(DISTINCT(MEMBER.ZDISPLAYFULLNAME)) AS 'CHAT_MEMBERS',
                group_concat(DISTINCT(MEMBER.ZPHONE)) AS 'CHAT_PHONES'
            FROM ZVIBERMESSAGE,ZCONVERSATION
                LEFT JOIN
                    (SELECT ZMEMBER.ZDISPLAYFULLNAME, ZMEMBER.Z_PK, ZPHONENUMBER.ZPHONE FROM ZMEMBER LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
                    UNION
                    SELECT ZMEMBER.ZDISPLAYFULLNAME, ZMEMBER.Z_PK, ZPHONENUMBER.ZPHONE FROM ZPHONENUMBER LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER = ZMEMBER.Z_PK
                    ) AS MEMBER ON MEMBER.Z_PK = MEMBER_ID
            WHERE ZVIBERMESSAGE.ZCONVERSATION = ZCONVERSATION.Z_PK
            GROUP BY ZVIBERMESSAGE.ZCONVERSATION
            ) CHATS ON ZVIBERMESSAGE.ZCONVERSATION = CHATS.ZCONVERSATION
        LEFT JOIN
            (SELECT ZMEMBER.ZDISPLAYFULLNAME, ZMEMBER.ZDISPLAYSHORTNAME, ZPHONENUMBER.ZPHONE, ZMEMBER.Z_PK
            FROM ZMEMBER LEFT JOIN ZPHONENUMBER ON ZMEMBER.Z_PK = ZPHONENUMBER.ZMEMBER
            UNION
            SELECT ZMEMBER.ZDISPLAYFULLNAME, ZMEMBER.ZDISPLAYSHORTNAME, ZPHONENUMBER.ZPHONE, ZMEMBER.Z_PK
            FROM ZPHONENUMBER LEFT JOIN ZMEMBER ON ZPHONENUMBER.ZMEMBER = ZMEMBER.Z_PK
            ) AS CHAT_MEMBER ON ZVIBERMESSAGE.ZPHONENUMINDEX = CHAT_MEMBER.Z_PK
        LEFT JOIN
            (SELECT ZRECENT.ZDURATION, ZRECENT.ZCALLLOGMESSAGE, ZRECENT.ZDATE, ZRECENT.ZCALLTYPE
            FROM ZRECENT) AS RECENT ON ZVIBERMESSAGE.Z_PK = RECENT.ZCALLLOGMESSAGE 
        LEFT JOIN ZVIBERLOCATION ON ZVIBERMESSAGE.ZLOCATION = ZVIBERLOCATION.Z_PK
        LEFT JOIN ZATTACHMENT ON ZVIBERMESSAGE.ZATTACHMENT = ZATTACHMENT.Z_PK
        ORDER BY ZVIBERMESSAGE.Z_PK
    '''

    db_records = get_sqlite_db_records(source_path, query)

    if db_records:
        logfunc(f"Found {len(db_records)} chat messages")
    else:
        logfunc("No chat messages found (db_records is empty)")

    for row in db_records:
        chat_members = f"{row[4]},{user_settings.get('_myUserName','')}"
        chat_phones = f"{row[5]},{user_settings.get('_myPhoneNumber','')}"
        
        sender_name = row[0]
        sender_phone = row[2]
        state = row[10]

        if state == 'Outgoing':
            sender_name = user_settings.get('_myUserName', 'Local User')
            sender_phone = user_settings.get('_myPhoneNumber', '')

        # Timestamps
        msg_create_date = convert_cocoa_core_data_ts_to_utc(row[6])
        msg_change_date = convert_cocoa_core_data_ts_to_utc(row[7])
        call_date = convert_cocoa_core_data_ts_to_utc(row[8])
        bomb_timestamp = convert_cocoa_core_data_ts_to_utc(row[25])

        metadata_blob = row[13]
        metadata_text = ""
        lat = row[18]
        lon = row[19]

        if metadata_blob:
            try:
                y = json.loads(metadata_blob, strict=False)
                
                try:
                    if lat is None: lat = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Latitude']
                    if lon is None: lon = y['pa_message_data']['rich_media']['Buttons'][2]['Map']['Longitude']
                except (KeyError, IndexError, TypeError):
                    pass
                
                meta_parts = []
                if "Text" in y: meta_parts.append(f"Text: {y['Text']}")
                if "Title" in y: meta_parts.append(f"Title: {y['Title']}")
                if "URL" in y: meta_parts.append(f"URL: {y['URL']}")
                if "ThumbnailURL" in y: meta_parts.append(f"ThumbnailURL: {y['ThumbnailURL']}")
                if "Type" in y: meta_parts.append(f"Type: {y['Type']}")
                
                metadata_text = ", ".join(meta_parts)
            except Exception:
                pass

        attachment_name = row[15]
        thumb_id = None
        if attachment_name and attachment_name in attachment_files:
            thumb_id = check_in_media(attachment_files[attachment_name], attachment_name)

        # Booleans
        chat_deleted = 'True' if row[20] == 1 else 'False'
        msg_deleted = 'True' if row[21] == 1 else 'False'
        chat_fav = 'True' if row[25] == 1 else 'False'

        data_list.append((
            msg_create_date,
            sender_name, row[1], sender_phone,
            row[3], chat_members, chat_phones,
            msg_change_date, row[14], thumb_id, attachment_name, 
            call_date, row[9], state, row[11],
            row[12], row[16], row[17],
            lat, lon,
            chat_deleted, msg_deleted,
            row[22], row[23], bomb_timestamp,
            chat_fav, row[26], metadata_text
        ))

    data_headers = (
        ('Timestamp', 'datetime'), 
        'Sender Name', 'Sender Short Name', 'Sender Phone',
        'Chat Name', 'Participants', 'Participant Phones',
        ('Message Changed', 'datetime'), 'Message Content', ('Attachment', 'media'), 'Attachment Name',
        ('Call Date', 'datetime'), 'Call Type', 'State', 'Duration',
        'System Type', 'Attachment Type', 'Attachment Size',
        'Latitude', 'Longitude',
        'Chat Deleted', 'Message Deleted',
        'Chat TimeBomb', 'Message TimeBomb', ('Message TimeBomb TS', 'datetime'),
        'Chat Favorite', 'Likes', 'Metadata Fragments'
    )
    
    if not data_list:
        logfunc("No data found for Viber - Chats")
        return data_headers, [], source_path

    return data_headers, data_list, source_path
