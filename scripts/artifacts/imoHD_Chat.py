__artifacts_v2__ = {
    "imoHDChatMessages": {
        "name": "IMO HD Chat - Messages",
        "description": "IMO HD chat messages and attachments",
        "author": "@stark4n6", "creation_date": "2026-06-23", "last_update_date": "2026-07-31", "requirements": "none",
        "category": "IMO HD Chat", "notes": "URLs are constructed by the parser from object IDs using an observed IMO CDN pattern; they are not stored in the data.",
        "paths": ('*/IMODb2.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/videos/*.webp'),
        "output_types": "standard", "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat BUID",
                "conversationLabelColumn": "Chat Name",
                "textColumn": "Message",
                "senderColumn": "Sender Name",
                "directionColumn": "Message Status",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "mediaColumn": "Attachment"
            }
        },
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | imo video calls and chat HD 7.2.23 | 38 rows",
            "hickman_ios13": "iOS 13.3.1 | imo video calls and chat HD 7.1.88, group.co.babypenguin | 5 rows",
            "hickman_ios14": "iOS 14.3 | imo video calls and chat HD 7.2.8, group.co.babypenguin | 9 rows",
        }
    },
    "imoHDChatContacts": {
        "name": "IMO HD Chat - Contacts",
        "description": "IMO HD chat contacts",
        "author": "@stark4n6", "creation_date": "2026-06-23", "last_update_date": "2026-07-31", "requirements": "none",
        "category": "IMO HD Chat", "notes": "URLs are constructed by the parser from object IDs using an observed IMO CDN pattern; they are not stored in the data.",
        "paths": ('*/IMODb2.sqlite*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | imo video calls and chat HD 7.2.23 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | group.co.babypenguin | 2 rows",
            "hickman_ios14": "iOS 14.3 | group.co.babypenguin | 3 rows",
        }
    },
    "imoHDChatKeyValues": {
        "name": "IMO HD Chat - Key Values",
        "description": "IMO HD account and application key/value records",
        "author": "@stark4n6", "creation_date": "2026-08-11", "last_update_date": "2026-08-11", "requirements": "none",
        "category": "IMO HD Chat", "notes": "Includes local account identifiers and other IMO key/value settings stored in ZIMOKEYVAL.",
        "paths": ('*/IMODb2.sqlite*',),
        "output_types": "standard", "artifact_icon": "key",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | imo video calls and chat HD 7.2.23 | 6 rows",
        }
    }
}

import io
import plistlib

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, check_in_media, logfunc

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)
_KEY_VALUE_CACHE = {}


def _load_blob_plist(blob):
    """Decode a ZIMDATA value blob: NSKeyedArchiver via nska_deserialize, otherwise plain plist."""
    if blob is None:
        return None
    obj = io.BytesIO(blob)
    if blob.find(b'NSKeyedArchiver') == -1:
        try:
            return plistlib.load(obj)
        except (plistlib.InvalidFileException, ValueError, OSError):
            return None
    try:
        return nd.deserialize_plist(obj)
    except _PLIST_ERRORS as ex:
        logfunc(f'IMO HD Chat: failed to read plist, error was: {ex}')
        return None


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('IMODb2.sqlite'):
            return file_found
    return ''


def _format_blob_value(blob):
    if blob is None:
        return ''
    parsed = _load_blob_plist(blob)
    if parsed is not None:
        return str(parsed)
    if isinstance(blob, bytes):
        return f'{len(blob)} bytes: {blob[:64].hex()}'
    return str(blob)


def get_imo_hd_key_values(db_path):
    """Return parsed ZIMOKEYVAL rows for reuse by IMO HD artifacts."""
    if not db_path:
        return []
    if db_path in _KEY_VALUE_CACHE:
        return _KEY_VALUE_CACHE[db_path]

    query = '''
    SELECT
        ZKEY,
        ZSTRING_VAL,
        ZLONG_VAL,
        ZDATE_VAL,
        ZDATA_VAL
    FROM ZIMOKEYVAL
    ORDER BY ZKEY
    '''
    key_values = []
    for row in get_sqlite_db_records(db_path, query):
        key_values.append({
            'key': row[0],
            'string_value': row[1],
            'long_value': row[2],
            'date_value': row[3],
            'data_value': _format_blob_value(row[4]),
        })
    _KEY_VALUE_CACHE[db_path] = key_values
    return key_values


def _get_key_value(key_values, key):
    for item in key_values:
        if item.get('key') == key:
            return item.get('string_value') or item.get('long_value') or item.get('data_value') or ''
    return ''


@artifact_processor
def imoHDChatMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Message Status',
        'Sender Name',
        'Chat Name',
        'Message',
        ('Attachment', 'media'),
        'Chat BUID',
        'Sender ID',
        'Sender Alias',
        ('Sender Phone', 'phonenumber'),
        'Item Action',
        'Constructed CDN URL (unverified)',
    )
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''
    files = [str(f) for f in context.get_files_found()]
    key_values = get_imo_hd_key_values(db_path)
    local_user_name = _get_key_value(key_values, 'imo_account_alias') or 'Local User'
    local_user_id = _get_key_value(key_values, 'imo_account_uid')

    query = '''
    SELECT
        CASE ZIMOCHATMSG.ZTS WHEN 0 THEN '' ELSE datetime(ZTS/1000000000, 'unixepoch') END,
        ZIMOCHATMSG.ZBUID,
        COALESCE(chat_contact.ZDISPLAY, ZIMOCHATMSG.ZCONTACT_ALIAS, ZIMOCHATMSG.ZALIAS),
        ZIMOCHATMSG.ZA_UID,
        COALESCE(sender_contact.ZDISPLAY, ZIMOCHATMSG.ZCONTACT_ALIAS, ZIMOCHATMSG.ZALIAS),
        ZIMOCHATMSG.ZALIAS,
        sender_contact.ZDIGIT_PHONE,
        ZIMOCHATMSG.ZTEXT,
        CASE ZIMOCHATMSG.ZISSENT WHEN 0 THEN 'Received' WHEN 1 THEN 'Sent' END,
        ZIMOCHATMSG.ZIMDATA
    FROM ZIMOCHATMSG
    LEFT JOIN ZIMOCONTACT AS chat_contact ON chat_contact.ZBUID = ZIMOCHATMSG.ZBUID
    LEFT JOIN ZIMOCONTACT AS sender_contact ON sender_contact.ZBUID = ZIMOCHATMSG.ZA_UID
    '''
    for row in get_sqlite_db_records(db_path, query):
        item_action = ''
        attachment_url = ''
        media_ref = ''
        plist = _load_blob_plist(row[9])
        if isinstance(plist, dict):
            item_action = plist.get('type', '')
            objects = plist.get('objects')
            if objects and isinstance(objects[0], dict):
                attachment_name = objects[0].get('object_id')
                if attachment_name:
                    attachment_url = f'https://cdn.imoim.us/s/object/{attachment_name}/'
                    for match in files:
                        if attachment_name in match:
                            media_ref = check_in_media(match)
                            break
        sender_id = local_user_id if row[8] == 'Sent' else row[3]
        sender_name = local_user_name if row[8] == 'Sent' else row[4]
        data_list.append((
            row[0],
            row[8],
            sender_name,
            row[2],
            row[7],
            media_ref,
            row[1],
            sender_id,
            row[5],
            row[6],
            item_action,
            attachment_url,
        ))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def imoHDChatContacts(context):
    data_headers = ('Contact Name', 'Contact Alias', ('Contact Phone', 'phonenumber'),
                    'Constructed Profile CDN URL (unverified)', 'User ID', 'Is Group')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        ZPH_NAME,
        ZALIAS,
        ZPHONE,
        'https://cdn.imoim.us/s/object/' || ZICON_ID || '/',
        ZBUID,
        CASE ZIS_GROUP WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' ELSE '' END
    FROM ZIMOCONTACT
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def imoHDChatKeyValues(context):
    data_headers = ('Key', 'String Value', 'Long Value', 'Date Value', 'Data Value')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    for item in get_imo_hd_key_values(db_path):
        data_list.append((item.get('key'), item.get('string_value'), item.get('long_value'),
                          item.get('date_value'), item.get('data_value')))

    return data_headers, data_list, context.get_relative_path(db_path)
