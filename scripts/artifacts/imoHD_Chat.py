__artifacts_v2__ = {
    "imoHDChatMessages": {
        "name": "IMO HD Chat - Messages",
        "description": "IMO HD chat messages and attachments",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "IMO HD Chat", "notes": "",
        "paths": ('*/IMODb2.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/videos/*.webp'),
        "output_types": "standard", "artifact_icon": "message-circle",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | imo video calls and chat HD 7.2.23 | 38 rows",
            "hickman_ios13": "iOS 13.3.1 | imo video calls and chat HD 7.1.88, group.co.babypenguin | 5 rows",
            "hickman_ios14": "iOS 14.3 | imo video calls and chat HD 7.2.8, group.co.babypenguin | 9 rows",
        }
    },
    "imoHDChatContacts": {
        "name": "IMO HD Chat - Contacts",
        "description": "IMO HD chat contacts",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "IMO HD Chat", "notes": "",
        "paths": ('*/IMODb2.sqlite*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | imo video calls and chat HD 7.2.23 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | group.co.babypenguin | 2 rows",
            "hickman_ios14": "iOS 14.3 | group.co.babypenguin | 3 rows",
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


@artifact_processor
def imoHDChatMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'Sender Name', 'Sender Alias', 'Sender Phone',
                    'Message', 'Message Status', 'Item Action', 'Attachment URL',
                    ('Attachment', 'media'))
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''
    files = [str(f) for f in context.get_files_found()]

    query = '''
    SELECT
        CASE ZIMOCHATMSG.ZTS WHEN 0 THEN '' ELSE datetime(ZTS/1000000000, 'unixepoch') END,
        ZIMOCONTACT.ZDISPLAY,
        ZIMOCHATMSG.ZALIAS,
        ZIMOCONTACT.ZDIGIT_PHONE,
        ZIMOCHATMSG.ZTEXT,
        CASE ZIMOCHATMSG.ZISSENT WHEN 0 THEN 'Received' WHEN 1 THEN 'Sent' END,
        ZIMOCHATMSG.ZIMDATA
    FROM ZIMOCHATMSG
    LEFT JOIN ZIMOCONTACT ON ZIMOCONTACT.ZBUID = ZIMOCHATMSG.ZA_UID
    '''
    for row in get_sqlite_db_records(db_path, query):
        item_action = ''
        attachment_url = ''
        media_ref = ''
        plist = _load_blob_plist(row[6])
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
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], item_action,
                          attachment_url, media_ref))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def imoHDChatContacts(context):
    data_headers = ('Contact Name', 'Contact Alias', 'Contact Phone', 'Profile Pic URL', 'User ID')
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
        ZBUID
    FROM ZIMOCONTACT
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)
