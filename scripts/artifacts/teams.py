__artifacts_v2__ = {
    "teamsMessages": {
        "name": "Teams Messages",
        "description": "Microsoft Teams messages and shared media",
        "author": "",
        "last_update_date": "2026-06-12",
        "requirements": "nska_deserialize",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',
                 '*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/Downloads/*/Images/*'),
        "output_types": "standard",
        "data_views": {
            "table": {},
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "conversationLabelColumn": "Thread Name",
                "textColumn": "Message",
                "senderColumn": "Display Name",
                "directionColumn": "Sent By Me",
                "directionSentValue": 1,
                "timeColumn": "Timestamp",
                "mediaColumn": "Media",
                #"sentMessageStaticLabel": "This Device" 
            }
        }
    },
    "teamsContacts": {
        "name": "Teams Contacts",
        "description": "Microsoft Teams contact list",
        "author": "",
        "last_update_date": "2026-06-12",
        "requirements": "nska_deserialize",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsUser": {
        "name": "Teams User Information",
        "description": "Microsoft Teams user profile and sync data",
        "author": "",
        "last_update_date": "2026-06-12",
        "requirements": "nska_deserialize",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsCalls": {
        "name": "Teams Call Logs",
        "description": "Microsoft Teams call history",
        "author": "",
        "last_update_date": "2026-06-12",
        "requirements": "nska_deserialize",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "standard"
    },
    "teamsLocations": {
        "name": "Teams Shared Locations",
        "description": "Microsoft Teams shared location data",
        "author": "",
        "last_update_date": "2026-06-12",
        "requirements": "nska_deserialize",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*',),
        "output_types": "all"
    }
}

import sqlite3
import json
import re
import datetime
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_ts_human_to_utc,
    get_plist_content,
    get_plist_file_content,
    logfunc,
    open_sqlite_db_readonly
)


def _convert_teams_timestamp(timestamp):
    if not timestamp:
        return ''
    return convert_ts_human_to_utc(str(timestamp).replace('T', ' ').rstrip('Z'))


def _get_first_image_source(content):
    if not content:
        return ''

    match = re.search(
        r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    return match.group(1) if match else ''


def _get_display_message(content):
    if not content:
        return ''

    emoji_match = re.search(
        r'<img\b(?=[^>]*\bitemtype\s*=\s*["\']http://schema\.skype\.com/Emoji["\'])'
        r'(?=[^>]*\balt\s*=\s*["\']([^"\']+)["\'])[^>]*>',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    if not emoji_match:
        return content

    content_without_emoji = content[:emoji_match.start()] + content[emoji_match.end():]
    remaining_text = re.sub(r'<[^>]+>', '', content_without_emoji).strip()
    return emoji_match.group(1) if not remaining_text else content


def _find_cached_media_path(files_found, cached_path):
    if not cached_path:
        return None

    normalized_cached_path = str(cached_path).replace('\\', '/')
    marker = '/SkypeSpacesDogfood/'
    cached_suffix = (
        f'SkypeSpacesDogfood/{normalized_cached_path.split(marker, 1)[1]}'
        if marker in normalized_cached_path
        else ''
    )

    normalized_files = [
        (file_found, str(file_found).replace('\\', '/'))
        for file_found in files_found
    ]

    if cached_suffix:
        for file_found, normalized_file in normalized_files:
            if normalized_file.endswith(cached_suffix):
                return file_found

    cached_name = normalized_cached_path.rsplit('/', 1)[-1]
    for file_found, normalized_file in normalized_files:
        if normalized_file.rsplit('/', 1)[-1] == cached_name:
            return file_found

    return None


@artifact_processor
def teamsMessages(context):
    files_found = context.get_files_found()
    if not files_found:
        return (), [], ''
    
    data_list = []
    cache_file = None
    db_file = None
    
    # Find required files
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            db_file = file_found
        elif file_found.endswith('CacheFile'):
            cache_file = file_found
    
    if not db_file:
        return (), [], files_found[0]
    
    # Initialize cache dictionary
    nsplist = {}
    if cache_file:
        nsplist = get_plist_file_content(cache_file)
        if not isinstance(nsplist, dict):
            nsplist = {}
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row  # Enable dictionary cursor
    
    cursor.execute('''
        SELECT
            datetime('2001-01-01', "ZARRIVALTIME" || ' seconds') as timestamp,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZFROM,
            ZTHREADID,
            ZTHREADTYPE,
            t.ZTHREADTOPIC,
            t.ZTSID,
            COALESCE(t.ZTHREADTOPIC, ZTHREADTYPE || ' ' || ZTHREADID) as thread_name,
            ZTS_MESSAGEBASETYPE,
            ZTS_MESSAGECONTENTTYPE,
			ZTS_ISSENTBYME
        FROM ZSMESSAGE m
        LEFT JOIN ZTHREAD t ON m.ZTHREADID = t.ZTSID
        ORDER BY timestamp
    ''')

    for row in cursor:
        timestamp = _convert_teams_timestamp(row['timestamp'])
        media_ref = None
        raw_message = row['ZCONTENT'] or ''
        display_message = _get_display_message(raw_message)
        
        # Process the first cached image associated with the message.
        image_url = _get_first_image_source(raw_message)
        if image_url:
            try:
                cached_path = nsplist.get(image_url, '')
                media_path = _find_cached_media_path(files_found, cached_path)
                if media_path:
                    media_ref = check_in_media(str(media_path))
            except (AttributeError, OSError, TypeError, ValueError) as ex:
                logfunc(f'Error processing image for message at {timestamp}: {ex}')
        
        data_list.append((
            timestamp,
            row['ZIMDISPLAYNAME'] or '',
            display_message,
            raw_message,
            row['ZFROM'] or '',
            row['ZTHREADID'] or '',
            row['ZTHREADTYPE'] or '',
            row['ZTHREADTOPIC'] or '',
            row['ZTSID'] or '',
            row['thread_name'] or '',
            row['ZTS_MESSAGEBASETYPE'] or '',
            row['ZTS_MESSAGECONTENTTYPE'] or '',
			row['ZTS_ISSENTBYME'],
            media_ref
        ))
    
    db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'),
        'Display Name',
        'Message',
        'Raw Message',
        'Sender',
        'Thread ID',
        'Thread Type',
        'Thread Topic',
        'Thread TSID',
        'Thread Name',
        'Message Base Type',
        'Message Content Type',
        'Sent By Me',
        ('Media', 'media')
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsContacts(context):
    files_found = context.get_files_found()
    if not files_found:
        return (), [], ''
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        return (), [], files_found[0]
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row

    cursor.execute('''
        SELECT
            ZDISPLAYNAME,
            ZEMAIL,
            ZPHONENUMBER
        FROM ZDEVICECONTACTHASH
    ''')
    
    for row in cursor:
        display_name = row['ZDISPLAYNAME'] if row['ZDISPLAYNAME'] else ''
        email = row['ZEMAIL'] if row['ZEMAIL'] else ''
        
        # Clean phone number
        phone = row['ZPHONENUMBER'] if row['ZPHONENUMBER'] else ''
        if phone:
            # Remove common formatting characters
            phone = phone.replace('(', '').replace(')', '').replace('-', '')
            phone = phone.replace(' ', '').replace('.', '')
    
        data_list.append((display_name, email, phone))
    
    db.close()
    
    data_headers = (
        'Display Name',
        'Email',
        ('Phone Number', 'phonenumber')
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsUser(context):
    files_found = context.get_files_found()
    if not files_found:
        return (), [], ''
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        return (), [], files_found[0]
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row
    
    cursor.execute('''
        SELECT
            datetime('2001-01-01', "ZTS_LASTSYNCEDAT" || ' seconds') as lastsyncedat,
            ZDISPLAYNAME,
            ZTELEPHONENUMBER
        FROM ZUSER
    ''')
    
    for row in cursor:
        data_list.append((
            _convert_teams_timestamp(row['lastsyncedat']),
            row['ZDISPLAYNAME'] if row['ZDISPLAYNAME'] else '',
            row['ZTELEPHONENUMBER'] if row['ZTELEPHONENUMBER'] else ''
        ))
    
    db.close()
    
    data_headers = (
        ('Timestamp Last Sync', 'datetime'),
        'Display Name',
        ('Phone Number', 'phonenumber')
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsCalls(context):
    files_found = context.get_files_found()
    if not files_found:
        return (), [], ''
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        return (), [], files_found[0]
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row
    
    cursor.execute('''
        SELECT
            ZCOMPOSETIME,
            ZFROM,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZPROPERTIES
        FROM ZSMESSAGE
        JOIN ZMESSAGEPROPERTIES ON ZSMESSAGE.ZTSID = ZMESSAGEPROPERTIES.ZTSID
        WHERE ZPROPERTIES IS NOT NULL
        ORDER BY ZCOMPOSETIME
    ''')
    
    for row in cursor:
        plist = get_plist_content(row['ZPROPERTIES'])
        if not isinstance(plist, dict):
            continue

        if 'call-log' not in plist:
            continue

        try:
            if isinstance(plist['call-log'], dict):
                datacalls = plist['call-log']
            else:
                datacalls = json.loads(plist['call-log'])

            call_start = _convert_teams_timestamp(datacalls.get('startTime'))
            call_connect = _convert_teams_timestamp(datacalls.get('connectTime'))
            call_end = _convert_teams_timestamp(datacalls.get('endTime'))

            data_list.append((
                call_start,
                call_connect,
                call_end,
                datacalls.get('callDirection', ''),
                datacalls.get('callType', ''),
                datacalls.get('callState', ''),
                datacalls.get('originator', ''),
                datacalls.get('target', ''),
                datacalls.get('originatorParticipant', {}).get('displayName', ''),
                datacalls.get('targetParticipant', {}).get('displayName', '')
            ))
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as ex:
            logfunc(f'Error processing call log data: {ex} - Data: {plist["call-log"]}')
    
    db.close()
    
    data_headers = (
        ('Call Start', 'datetime'),
        ('Call Connect', 'datetime'),
        ('Call End', 'datetime'),
        'Call Direction',
        'Call Type',
        'Call State',
        'Call Originator',
        'Call Target',
        'Call Originator Name',
        'Call Participant Name'
    )
    
    return data_headers, data_list, db_file

@artifact_processor
def teamsLocations(context):
    files_found = context.get_files_found()
    if not files_found:
        return (), [], ''
    
    data_list = []
    db_file = None
    
    for file_found in files_found:
        if file_found.endswith('.sqlite'):
            db_file = file_found
            break
    
    if not db_file:
        return (), [], files_found[0]
    
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row
    
    cursor.execute('''
        SELECT
            ZCOMPOSETIME,
            ZFROM,
            ZIMDISPLAYNAME,
            ZCONTENT,
            ZPROPERTIES
        FROM ZSMESSAGE
        JOIN ZMESSAGEPROPERTIES ON ZSMESSAGE.ZTSID = ZMESSAGEPROPERTIES.ZTSID
        WHERE ZPROPERTIES IS NOT NULL
        ORDER BY ZCOMPOSETIME
    ''')
    
    for row in cursor:
        compose_time = _convert_teams_timestamp(row['ZCOMPOSETIME'])
        plist = get_plist_content(row['ZPROPERTIES'])
        if not isinstance(plist, dict):
            continue

        if 'cards' not in plist:
            continue

        try:
            cards = json.loads(plist['cards'])
            card = cards[0]['content']['body'][0]

            card_url = card.get('selectAction', {}).get('url', '')
            card_title = card.get('selectAction', {}).get('title', '')
            card_text = cards[0]['content']['body'][1].get('text', '')
            card_url2 = card.get('url', '')

            card_lat = None
            card_long = None
            card_expires = None
            card_devid = None

            if card.get('id'):
                try:
                    id_content = json.loads(card['id'])
                    card_lat = id_content.get('latitude')
                    card_long = id_content.get('longitude')
                    expires_ms = id_content.get('expiresAt')
                    if expires_ms:
                        card_expires = datetime.datetime.fromtimestamp(
                            expires_ms / 1000,
                            tz=datetime.timezone.utc
                        )
                    card_devid = id_content.get('deviceId')
                except (AttributeError, TypeError, ValueError, OverflowError, OSError) as ex:
                    logfunc(f'Error processing card ID data: {ex}')

            data_list.append((
                compose_time,
                row['ZFROM'] if row['ZFROM'] else '',
                row['ZIMDISPLAYNAME'] if row['ZIMDISPLAYNAME'] else '',
                row['ZCONTENT'] if row['ZCONTENT'] else '',
                card_url,
                card_title,
                card_text,
                card_url2,
                card_lat,
                card_long,
                card_expires,
                card_devid
            ))
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as ex:
            logfunc(f'Error processing card data: {ex}')
    
    db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'),
        'Sender',
        'Display Name',
        'Content',
        'Card URL',
        'Card Title',
        'Card Text',
        'Card URL2',
        'Latitude',
        'Longitude',
        ('Card Expires', 'datetime'),
        'Device ID'
    )
    
    return data_headers, data_list, db_file
    
